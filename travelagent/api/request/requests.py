"""Module for API requests classes."""

from typing import List, Literal

from pydantic import Field

from travelagent.api.request import IdentifiableRequest


class TravelPlanRequest(IdentifiableRequest):
    """Class implementing the TravelPlanRequest for plan endpoints."""

    departure: str = Field(default=..., description="Departure city. It must be one of the locations in Noleggiare.it list.")
    arrival: str = Field(default=..., description="Arrival city. It must be one of the locations in Noleggiare.it list.")
    duration_value: int = Field(default=..., description="Travel duration expressed in days")
    interests: Literal['outdoor', 'culture', 'food', 'nightlife'] = Field(default=..., description="Interests used to suggest intermediate stages")
