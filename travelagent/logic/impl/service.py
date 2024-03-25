"""Completion Service classes module."""

import time
from typing import Dict, Optional

from aramix.application.commons.metrics.collector.collectors import BaseMetricsCollector
from aramix.application.commons.metrics.handler.handlers import (
    WithMetricCollectorHandler,
)
from hexagonal.core.domain.port.ports import BasePort, OutputPort
from hexagonal.core.domain.service.services import BaseService

from travelagent.logic.models import TravelPlanInput, TravelPlanOutput, TravelPlanDurationEvent
from travelagent.logic.process.agent import BaseTravelAgent
from travelagent.logic.usecases import TravelPlannerUseCase


class TravelPlannerService(
    BaseService[OutputPort], TravelPlannerUseCase, WithMetricCollectorHandler
):
    """Class implementing the TravelPlannerService for planning travels based on input data."""

    def __init__(
        self,
        ports: Dict[str, BasePort] | None,
        agent: BaseTravelAgent,
        collector: Optional[BaseMetricsCollector] = None,
    ) -> None:
        """Initialize the class.

        :param ports: the ports registry to be used in the service.
        :param agent: the agent instance to be used in the service.
        :param collector: the collector to be used for metrics collecting.

        """
        BaseService.__init__(self, "travel-planner-service", "TravelPlanner Service", ports)
        TravelPlannerUseCase.__init__(self)
        WithMetricCollectorHandler.__init__(self, collector)
        self._agent = agent

    def _validate_registry(self) -> bool:
        """Validate the service registry.

        :return: True if the registry is validated.
        """
        return not bool(self.registry)

    def _measure(self, uuid: str, duration: int) -> None:
        """Measure the process.

        :param uuid: the unique identifier of the request.
        :param duration: the duration in milliseconds.
        """
        try:
            if self.is_collectable and self.metric_logger is not None:
                metric = TravelPlanDurationEvent(
                    name="duration-travel-planner",
                    uuid=uuid,
                    service=self.name,
                    operation="plan",
                    duration=duration,
                )
                self.metric_logger.collect(metric.json())
        except Exception as e:
            self.logger.error(e)

    async def plan(self, data: TravelPlanInput) -> TravelPlanOutput:
        """Embed input texts.

        :param data: input data.
        :return: planned travel description.
        """
        self.logger.info(
            f"Planning travel using '{self._agent.name}' agent for a travel starting from {data.departure} and "
            f"arriving to {data.arrival} with duration of {data.duration_value} days and {data.interests} interests"
        )
        start_time = round(time.time() * 1000)
        result = await self._agent.plan(data)
        end_time = round(time.time() * 1000)
        self._measure(data.uuid, end_time - start_time)
        return result
