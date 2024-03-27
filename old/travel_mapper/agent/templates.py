from textwrap import dedent

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List


class Trip(BaseModel):
    start: str = Field(description="start location of trip")
    end: str = Field(description="end location of trip")
    waypoints: List[str] = Field(description="list of waypoints")
    transit: str = Field(description="mode of transportation")


class Validation(BaseModel):
    plan_is_valid: str = Field(
        description="This field is 'yes' if the plan is feasible, 'no' otherwise"
    )
    updated_request: str = Field(description="Your update to the plan")


class ValidationTemplate(object):
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=Validation)

        self.chat_prompt = ChatPromptTemplate.from_messages(
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
                        "format_instructions": self.parser.get_format_instructions()
                    },
                ),
                HumanMessagePromptTemplate.from_template(
                    "\n####{query}####",
                    input_variables=["query"]
                )
            ]
        )



class ItineraryTemplate(object):
    def __init__(self):

        self.chat_prompt =


class MappingTemplate(object):
    def __init__(self):


        self.parser = PydanticOutputParser(pydantic_object=Trip)


        self.chat_prompt =
