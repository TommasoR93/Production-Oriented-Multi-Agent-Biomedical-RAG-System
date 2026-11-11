from typing import Protocol, Mapping
from requests import Response

class Transport(Protocol):
    """Abstraction over HTTP requests"""
    def get(
            self,
            endpoint: str,
            params: Mapping[str, str | int]
            ) -> Response:
        """Perform a GET request"""