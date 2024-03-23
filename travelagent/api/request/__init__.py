"""Request module."""
from pydantic import BaseModel


class IdentifiableRequest(BaseModel):
    """Class implementing the IdentifiableRequest, used as a generic request.

    uid: the unique identifier of the request.
    """

    uuid: str