"""Responses classes module."""

from pydantic import BaseModel, Field


class TravelPlanResponse(BaseModel):
    """Class implementing the TravelPlan for a plan endpoint."""

    plan: str = Field(default=..., description="Travel plan description")
