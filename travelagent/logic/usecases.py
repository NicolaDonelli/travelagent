"""Usecases classes module."""

from abc import ABC

from hexagonal.core.domain.service.usecases import UseCase

from travelagent.logic.models import TravelPlanInput, TravelPlanOutput


class TravelPlannerUseCase(UseCase, ABC):
    """Class implementing the TravelPlannerUseCase use case."""

    def __init__(self) -> None:
        """
        Initialize the class.

        This use case consists in planning travels based on input data.
        """
        super().__init__(self.UID(), "TravelPlanner")

    @classmethod
    def UID(cls) -> str:
        """Define the UID class method.

        :return: the UID identifier of the class
        """
        return "travel-planner"

    async def plan(self, data: TravelPlanInput) -> TravelPlanOutput:
        """Build a travel plan based on input data.

        :param data: input data.
        :raises NotImplementedError: it raises for abstract class
        """
        raise NotImplementedError
