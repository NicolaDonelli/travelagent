from textwrap import dedent
from typing import Literal, List

from langchain.chains import LLMChain, SequentialChain
from langchain.llms import GooglePalm
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field

from .config import GoogleLLMConfig
from .langchain_wrapper import WithCredentialsGoogleGenerativeAI
from google.oauth2.service_account import Credentials
from travelagent.logic.process.agent import BaseTravelAgent
import time


class Validation(BaseModel):
    plan_is_valid: Literal['yes', 'no'] = Field(description="This field is 'yes' if the plan is feasible, 'no' otherwise")
    updated_request: str = Field(description="Your update to the plan")


class Trip(BaseModel):
    start: str = Field(description="start location of trip")
    end: str = Field(description="end location of trip")
    waypoints: List[str] = Field(description="list of waypoints")
    transit: str = Field(description="mode of transportation")


class GoogleTravelAgent(BaseTravelAgent):

    def __init__(
        self,
        config: GoogleLLMConfig,
    ):

        self.chat_model = WithCredentialsGoogleGenerativeAI(
            credentials=Credentials.from_service_account_info(config.sa_key),
            model=config.model_name,
            temperature=config.hparams.temperature,
            top_p=config.hparams.top_p,
            top_k=config.hparams.top_k,
            max_output_tokens=config.hparams.max_output_tokens,
            n=config.hparams.n,
            max_retries=config.hparams.max_retries,
            client_options=config.hparams.client_options,
            transport=config.hparams.transport,
            safety_settings=config.hparams.safety_settings
        )

        self.validation_parser = PydanticOutputParser(pydantic_object=Validation)
        self.mapping_parser = PydanticOutputParser(pydantic_object=Trip)

        self.validation_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    dedent(
                        """
                        You are a travel agent who helps users make exciting travel plans.
                        
                        The user's request will be denoted by four hashtags. Determine if the user's
                        request is reasonable and achievable within the constraints they set.
                        
                        A valid request should contain the following:
                        - A start and end location
                        - A trip duration that is reasonable given the start and end location
                        - Some other details, like the user's interests and/or preferred mode of transport
                        
                        Any request that contains potentially harmful activities is not valid, regardless of what
                        other details are provided.
                        
                        If the request is not vaid, set
                        plan_is_valid = 0 and use your travel expertise to update the request to make it valid,
                        keeping your revised request shorter than 100 words.
                        
                        If the request seems reasonable, then set plan_is_valid = 1 and
                        don't revise the request.
                        
                        {format_instructions}
                        """
                    ),
                    partial_variables={
                        "format_instructions": self.validation_parser.get_format_instructions()
                    },
                ),
                HumanMessagePromptTemplate.from_template(
                    "\n####{query}####",
                    input_variables=["query"]
                )
            ]
        )
        self.itinerary_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    dedent(
                        """
                        You are a travel agent who helps users make exciting travel plans.

                        The user's request will be denoted by four hashtags. Convert the
                        user's request into a detailed itinerary describing the places
                        they should visit and the things they should do.

                        Try to include the specific address of each location.

                        Remember to take the user's preferences and timeframe into account,
                        and give them an itinerary that would be fun and realistic given their constraints.

                        Try to make sure the user doesn't need to travel for more than 8 hours on any one day during
                        their trip.

                        Return the itinerary as a bulleted list with clear start and end locations and mention the type of transit for the trip.

                        If specific start and end locations are not given, choose ones that you think are suitable and give specific addresses.

                        Your output must be the list and nothing else.
                        """
                    ),
                ),
                HumanMessagePromptTemplate.from_template(
                    "\n####{query}####", input_variables=["query"]
                )
            ]
        )
        self.mapping_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    dedent(
                        """
                        You an agent who converts detailed travel plans into a simple list of locations.

                        The itinerary will be denoted by four hashtags. Convert it into
                        list of places that they should visit. Try to include the specific address of each location.

                        Your output should always contain the start and end point of the trip, and may also include a list
                        of waypoints. It should also include a mode of transit. The number of waypoints cannot exceed 20.
                        If you can't infer the mode of transit, make a best guess given the trip location.

                        For example:

                        ####
                        Itinerary for a 2-day driving trip within London:
                        - Day 1:
                        - Start at Buckingham Palace (The Mall, London SW1A 1AA)
                        - Visit the Tower of London (Tower Hill, London EC3N 4AB)
                        - Explore the British Museum (Great Russell St, Bloomsbury, London WC1B 3DG)
                        - Enjoy shopping at Oxford Street (Oxford St, London W1C 1JN)
                        - End the day at Covent Garden (Covent Garden, London WC2E 8RF)
                        - Day 2:
                        - Start at Westminster Abbey (20 Deans Yd, Westminster, London SW1P 3PA)
                        - Visit the Churchill War Rooms (Clive Steps, King Charles St, London SW1A 2AQ)
                        - Explore the Natural History Museum (Cromwell Rd, Kensington, London SW7 5BD)
                        - End the trip at the Tower Bridge (Tower Bridge Rd, London SE1 2UP)
                        #####

                        Output:
                        Start: Buckingham Palace, The Mall, London SW1A 1AA
                        End: Tower Bridge, Tower Bridge Rd, London SE1 2UP
                        Waypoints: ["Tower of London, Tower Hill, London EC3N 4AB", "British Museum, Great Russell St, Bloomsbury, London WC1B 3DG", "Oxford St, London W1C 1JN", "Covent Garden, London WC2E 8RF","Westminster, London SW1A 0AA", "St. James's Park, London", "Natural History Museum, Cromwell Rd, Kensington, London SW7 5BD"]
                        Transit: driving

                        Transit can be only one of the following options: "driving", "train", "bus" or "flight".

                        {format_instructions}
                        """
                    ),
                    partial_variables={
                        "format_instructions": self.mapping_parser.get_format_instructions()
                    },
                ),
                HumanMessagePromptTemplate.from_template(
                    "\n####{agent_suggestion}####", input_variables=["agent_suggestion"]
                )
            ]
        )

        self.validation_chain = self._set_up_validation_chain(self.logger.level <= 10)
        self.agent_chain = self._set_up_agent_chain(self.logger.level <= 10)

    @property
    def name(self) -> str:
        """Get the agent name.

        :returns: agent name.
        """
        return "GoogleTravelAgent"

    def _set_up_validation_chain(self, debug=True) -> SequentialChain:
        """

        Parameters
        ----------
        debug

        Returns
        -------

        """
        validation_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.validation_prompt,
            output_parser=self.validation_parser,
            output_key="validation_output",
            verbose=debug,
        )

        return SequentialChain(
            chains=[validation_agent],
            input_variables=["query", "format_instructions"],
            output_variables=["validation_output"],
            verbose=debug,
        )

    def _set_up_agent_chain(self, debug=True) -> SequentialChain:
        """

        Parameters
        ----------
        debug

        Returns
        -------

        """
        travel_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.itinerary_prompt,
            verbose=debug,
            output_key="agent_suggestion",
        )

        parser = LLMChain(
            llm=self.chat_model,
            prompt=self.mapping_prompt,
            output_parser=self.mapping_parser,
            verbose=debug,
            output_key="mapping_list",
        )

        return SequentialChain(
            chains=[travel_agent, parser],
            input_variables=["query", "format_instructions"],
            output_variables=["agent_suggestion", "mapping_list"],
            verbose=debug,
        )

    def suggest_travel(self, query):
        """

        Parameters
        ----------
        query

        Returns
        -------

        """
        self.logger.info("Validating query")
        t1 = time.time()
        self.logger.info(
            "Calling validation (model is {}) on user input".format(
                self.chat_model.model
            )
        )
        validation_result = self.validation_chain(
            {
                "query": query,
                "format_instructions": self.validation_parser.get_format_instructions(),
            }
        )

        validation_test = validation_result["validation_output"].dict()
        t2 = time.time()
        self.logger.info("Time to validate request: {}".format(round(t2 - t1, 2)))

        if validation_test["plan_is_valid"].lower() == "no":
            self.logger.warning("User request was not valid!")
            print("\n######\n Travel plan is not valid \n######\n")
            print(validation_test["updated_request"])
            return None, None, validation_result

        else:
            # plan is valid
            self.logger.info("Query is valid")
            self.logger.info("Getting travel suggestions")
            t1 = time.time()

            self.logger.info(
                "User request is valid, calling agent (model is {})".format(
                    self.chat_model.model
                )
            )

            agent_result = self.agent_chain(
                {
                    "query": query,
                    "format_instructions": self.mapping_parser.get_format_instructions(),
                }
            )

            trip_suggestion = agent_result["agent_suggestion"]
            list_of_places = agent_result["mapping_list"].dict()
            t2 = time.time()
            self.logger.info("Time to get suggestions: {}".format(round(t2 - t1, 2)))

            return trip_suggestion, list_of_places, validation_result
