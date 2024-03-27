"""Config classes module."""

import json
from typing import Dict, List, Optional, TypedDict, Any

from google.ai.generativelanguage_v1 import HarmCategory
from google.generativeai.types import HarmBlockThreshold
from py4ai.core.config.configurations import BaseConfig


class GoogleLLMHparams(BaseConfig):
    """Hyperparameters for Genai LLMs."""

    @property
    def temperature(self) -> float:
        """
        Get the temperature.

        Temperature controls the degree of randomness in token selection.

        :return: temperature value
        """
        return self.getValue("temperature")

    @property
    def max_output_tokens(self) -> int:
        """
        Get the max_output_tokens.

        Token limit determines the maximum amount of text output.

        :return: max_output_tokens value
        """
        return self.getValue("max_output_tokens")

    @property
    def top_p(self) -> int:
        """
        Get the top_p.

        Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value.

        :return: top_p value
        """
        return self.getValue("top_p")

    @property
    def top_k(self) -> int:
        """
        Get the top_k.

        Select the top_k most probable tokens each time.

        :return: top_p value
        """
        return self.getValue("top_k")

    @property
    def n(self) -> int:
        """
        Get the of chat completions to generate for each prompt.

        Note that the API may not return the full n completions if duplicates are generated.

        :return: number of completions to generate
        """
        return self.getValue("n")

    @property
    def max_retries(self) -> int:
        """
        Get the maximum number of retries to make when generating.

        :return: max retries value
        """
        return self.getValue("max_retries")

    @property
    def client_options(self) -> Optional[Dict[str, Any]]:
        """
        Get dictionary of client options to pass to the Google API client, such as `api_endpoint`.

        :return: client options
        """
        return self.safeGetValue("client_options")

    @property
    def transport(self) -> Optional[str]:
        """
        Get a string, one of: [`rest`, `grpc`, `grpc_asyncio`].

        :return: transport options
        """
        return self.safeGetValue("transport")

    @property
    def safety_settings(self) -> Optional[Dict[HarmCategory, HarmBlockThreshold]]:
        """
        Get the default safety settings to use for all generations.

        For example:

            from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory

            safety_settings = {
                HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }
        :return: safety settings
        """
        return self.safeGetValue("safety_settings")


class GoogleLLMConfig(BaseConfig):
    """Class implementing the HFPipeline config section."""

    @property
    def model_name(self) -> str:
        """
        Get the Google model name.

        :return: the model_id
        """
        return self.getValue("model_name")

    @property
    def sa_key(self) -> Dict[str, str]:
        """
        Get the Google credentials.

        :return: Google Credentials
        """
        if self.safeGetValue("sa_key") is None:
            with open(self.getValue("sa_key_path"), "r") as fil:
                key = json.load(fil)
        else:
            key = json.loads(self.safeGetValue("sa_key"))
        return key

    @property
    def hparams(self) -> GoogleLLMHparams:
        """
        Get the hparams for the model.

        :return: the hparams dict.
        """
        return GoogleLLMHparams(self.sublevel("hparams"))
