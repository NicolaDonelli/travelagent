"""TravelAgentMicroservice Configuration classes."""

from microservices.core.application.config import MicroserviceConfig, StorageConfig


class TravelAgentMicroserviceConfig(MicroserviceConfig):
    """Class implementing TravelAgentMicroserviceConfig.

    It overrides the base MicroserviceConfig for the Base Microservice class.
    """

    @property
    def storage(self) -> StorageConfig:
        """
        Get storage config.

        :return: storage config
        """
        return StorageConfig(self.sublevel("storage"))
