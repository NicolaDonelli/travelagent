"""TravelAgentMicroservice classes module."""

from fastapi.exceptions import RequestValidationError
from hexagonal.core.domain.service.facade import ServiceFacade
from microservices.core.application.api.exceptions import BadRequestExceptionHandler
from microservices.core.application.api.health.routes import HealthRoute
from microservices.core.application.api.memory.routes import MemoryRoute
from microservices.hexagonal.application.application import HexagonalMicroservice

from travelagent.ms.application.api.routes import TravelAgentRoute
from travelagent.ms.application.config import TravelAgentMicroserviceConfig


class TravelAgentMicroservice(HexagonalMicroservice):
    """Class implementing the LLM Microservice."""

    def __init__(
        self,
        config: TravelAgentMicroserviceConfig,
        facade: ServiceFacade | None = None,
    ) -> None:
        """Initialize the TravelAgentMicroservice class.

        :param config: the microservice configuration.
        :param facade: the facade for services.
        """
        self._facade = facade
        super().__init__(
            uid=config.uid, name=config.name, description=config.description
        )

    def _configure(self) -> None:
        """Configure the microservice defining routes and handlers."""
        health_route = HealthRoute("/system")
        self.register_api_router(health_route)
        memory_route = MemoryRoute("/system")
        self.register_api_router(memory_route)
        route = TravelAgentRoute(facade=self._facade)
        self.register_api_router(route)

        # Handlers
        self.register_error_handler(
            RequestValidationError,
            BadRequestExceptionHandler.handle_request_validation_error,
        )
