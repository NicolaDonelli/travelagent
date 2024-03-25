from typing import Literal, Optional

from pydantic import Field

from travelagent.api.request.requests import TravelPlanRequest
from travelagent.api.response.responses import TravelPlanResponse
from aramix.application.commons.metrics.collector.model import BaseMetricEvent


class TravelPlanInput(TravelPlanRequest):
    """Class implementing an input for travel planner use cases."""
    ...


class TravelPlanOutput(TravelPlanResponse):
    """Class implementing an output for travel planner use cases."""

    ...


class TravelPlanDurationEvent(BaseMetricEvent):
    """Class implementing the metric event model."""

    uuid: str = Field(default=..., description="Identifier of the .")
    service: str = Field(default=..., description="Service causing the event.")
    duration: int = Field(default=..., description="Event duration in units.")
    units: Literal["seconds", "milliseconds"] = Field(default="milliseconds", description="Event duration unit.")
    message: Optional[str] = Field(default=None, description="Event duration message.")

    @property
    def milliseconds(self) -> int:
        """Get duration property in milliseconds.

        :return: the duration in milliseconds.
        """
        return self.duration if self.units == "milliseconds" else self.duration * 1000

    @property
    def seconds(self) -> float:
        """Get duration property in seconds.

        :return: the duration in seconds.
        """
        return self.milliseconds / 1000

    @property
    def minutes(self) -> float:
        """Get duration property in minutes.

        :return: the duration in minutes.
        """
        return self.seconds / 60

    @property
    def hours(self) -> float:
        """Get duration property in hours.

        :return: the duration in hours.
        """
        return self.minutes / 60

    @property
    def days(self) -> float:
        """Get duration property in days.

        :return: the duration in days.
        """
        return self.hours / 24