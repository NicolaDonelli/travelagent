"""Agent class module."""

from abc import ABC, abstractmethod

from py4ai.core.logging import WithLogging

from travelagent.logic.models import TravelPlanInput, TravelPlanOutput


class BaseTravelAgent(WithLogging, ABC):
    """Class implementing the abstract BaseTravelAgent for generating travel plans."""

    @abstractmethod
    async def plan(self, data: TravelPlanInput) -> TravelPlanOutput:
        """Build a travel plan based on input data.

        :param data: input data.
        :return: travel plan description
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the agent name.

        :returns: agent name.
        """
        ...
