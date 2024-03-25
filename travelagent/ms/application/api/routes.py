"""Routes classes module."""

from datetime import datetime
from typing import Dict, List, Type, TypedDict

from fastapi import status
from hexagonal.core.domain.service.facade import ServiceFacade
from microservices.hexagonal.application.api.routes import HexagonalBaseRoute

from travelagent.api.request.requests import TravelPlanRequest
from travelagent.api.response.responses import TravelPlanResponse
from travelagent.logic.models import TravelPlanInput, TravelPlanOutput
from travelagent.logic.usecases import TravelPlannerUseCase
from microservices.core.application.api.exceptions import (
    InternalServerErrorException
)


class OtherParamsDict(TypedDict):
    """Other routes parameters dictionary."""

    path: str
    methods: List[str]
    description: str
    response_model: Type[TravelPlanResponse]
    status_code: int
    responses: Dict[int, Dict[str, str]]


class RouteParamsDict(TypedDict):
    """Routes parameters dictionary."""

    endpoint_name: str
    other: OtherParamsDict


class TravelAgentRoute(HexagonalBaseRoute):
    """Class implementing TravelAgentRoute for documents identifying."""

    endpoint_map: Dict[Type[TravelPlannerUseCase], RouteParamsDict] = {
        TravelPlannerUseCase: RouteParamsDict(
            endpoint_name="plan",
            other=OtherParamsDict(
                path="/plan",
                methods=["POST"],
                description="plan trip based on input data",
                response_model=TravelPlanResponse,
                status_code=status.HTTP_200_OK,
                responses={
                    status.HTTP_400_BAD_REQUEST: {"description": "Bad Request"},
                    status.HTTP_500_INTERNAL_SERVER_ERROR: {
                        "description": "Internal Server Error"
                    },
                },
            ),
        ),
    }

    def __init__(
        self,
        prefix: str = "/travelagent",
        startup_timestamp: datetime = datetime.utcnow(),
        facade: ServiceFacade | None = None,
    ) -> None:
        """Initialize the TravelAgentRoute class.

        :param prefix: the prefix to be used for the current route.
        :param startup_timestamp: the startup timestamp for the current route.
        :param facade: the application facade for services.
        """
        super().__init__(
            "travelagent-controller",
            "Travel Agent Controller",
            facade,
            prefix=prefix,
            startup_timestamp=startup_timestamp,
        )

    def _configure(self) -> None:
        for k, v in self.endpoint_map.items():
            if (
                self._facade is not None
                and self._facade._get_use_case(k().UID(), k) is not None
            ):
                self.add_api_route(
                    **dict(
                        v["other"], **{"endpoint": getattr(self, v["endpoint_name"])}
                    )
                )
                self.logger.info(f"Endpoint {v['other']['path']} successfully created")
            else:
                self.logger.info(
                    f"Endpoint {v['other']['path']} not created since there is no "
                    f"'{k.UID()}' use case implemented in the facade"
                )

    async def plan(self, request: TravelPlanRequest) -> TravelPlanResponse:
        """Define the complete POST endpoint.

        :param request: the request to be managed.
        :raises NotImplementedError: not implemented error.
        :raises InternalServerErrorException: internal server error.
        :return: the loader response
        """
        if self._facade:
            use_case = self._facade._get_use_case(
                TravelPlannerUseCase.UID(), TravelPlannerUseCase
            )
            if use_case is not None:
                try:
                    result: TravelPlanOutput = await use_case.plan(
                        data=TravelPlanInput(
                            uuid=request.uuid,
                            departure=request.departure,
                            arrival=request.arrival,
                            duration_value=request.duration_value,
                            interests=request.interests
                        )
                    )
                    return TravelPlanResponse(plan=result.plan)
                except Exception as e:
                    self.logger.error(str(e), exc_info=True)
                    raise InternalServerErrorException(str(e))

        raise NotImplementedError()
