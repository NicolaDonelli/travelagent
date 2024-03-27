from typing import Dict

import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from google.oauth2.service_account import Credentials
from langchain_google_genai.llms import GoogleModelFamily
from pydantic import root_validator


class WithCredentialsGoogleGenerativeAI(GoogleGenerativeAI):
    """Google GenerativeAI models.

    Example:
        .. code-block:: python

            from langchain_google_genai import GoogleGenerativeAI
            llm = GoogleGenerativeAI(model="gemini-pro")
    """

    credentials: Credentials  #: :meta private:

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validates params and passes them to google-generativeai package."""
        model_name = values["model"]

        safety_settings = values["safety_settings"]

        genai.configure(
            credentials=cls.credentials,
            transport=values.get("transport"),
            client_options=values.get("client_options"),
        )

        if safety_settings and (
            not GoogleModelFamily(model_name) == GoogleModelFamily.GEMINI
        ):
            raise ValueError("Safety settings are only supported for Gemini models")

        if GoogleModelFamily(model_name) == GoogleModelFamily.GEMINI:
            values["client"] = genai.GenerativeModel(
                model_name=model_name, safety_settings=safety_settings
            )
        else:
            values["client"] = genai

        if values["temperature"] is not None and not 0 <= values["temperature"] <= 1:
            raise ValueError("temperature must be in the range [0.0, 1.0]")

        if values["top_p"] is not None and not 0 <= values["top_p"] <= 1:
            raise ValueError("top_p must be in the range [0.0, 1.0]")

        if values["top_k"] is not None and values["top_k"] <= 0:
            raise ValueError("top_k must be positive")

        if values["max_output_tokens"] is not None and values["max_output_tokens"] <= 0:
            raise ValueError("max_output_tokens must be greater than zero")

        return values
