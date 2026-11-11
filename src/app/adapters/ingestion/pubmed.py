import logging
import time
from typing import Mapping
import requests
from requests import Session, Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.app.exceptions.ingestion import PubMedTimeOutError, PubMedTransportError, PubMedHTTPError
from src.app.config.settings import PubMedSettings

logger = logging.getLogger(__name__)

class PubMedRequestTransport:
    """Handles HTTP communications with the PubMed API.

    Provides session management, automatic retries, rate limit and methods for searching and fetching articles.

    Args:
        config: Configuration for PubMed API requests.
    """
    def __init__(self, config: PubMedSettings) -> None:
        self.config = config
        self.session = self.create_session()
        self.last_request_time : float = 0.0

    def create_session(self) -> Session:
        """Create an HTTP session with automatic retry handling."""

        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            allowed_methods=["GET"],
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()

        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def rate_limit(self) -> None:
        """Enforce the minimum interval between HTTP requests."""

        now = time.monotonic()
        elapsed = now - self.last_request_time
        if elapsed < self.config.request_interval:
            time.sleep(self.config.request_interval - elapsed)
        self.last_request_time = time.monotonic()

    def get(self, endpoint: str, params: Mapping[str, str | int]) -> Response:
        """Send a GET request to the PubMed API.

        Args:
            endpoint: PubMed API endpoint to request.
            params: Query parameters to include in the request.

        Returns:
            HTTP response from the PubMed API.
        
        Raises:
            PubMedTimeOutError: If the HTTP request times out.
            PubMedTransportError: If an HTTP transport error occurs.
            PubMedHTTPError: If the PubMed API returns an unseccessfull HTTP response.
        """
        self.rate_limit()
        logger.info("Pudmed request started", extra={"endpoint": endpoint})
        request_params = {
            **params,
            "api_key": self.config.pubmed_api_key
        }
        try:
            response = self.session.get(f"{self.config.base_url}/{endpoint}", params=request_params, timeout=10)
        except requests.Timeout as exc:
            logger.warning("PubMed Request timeout", extra={"endpoint": endpoint})
            raise PubMedTimeOutError(f"PubMed request Timeout error {exc}: {endpoint}")
        except requests.RequestException as exc:
            logger.warning("PubMed request transport error", extra={"endpoint": endpoint})
            raise PubMedTransportError(f"PubMed request Transport error {exc}: {endpoint}")
        if response.status_code != 200:
            logger.warning("PubMed response status code error", extra={"endpoint": endpoint})
            raise PubMedHTTPError(f"PubMed request HTTP error: {endpoint}")
        return response        

    def esearch(self, query: str, max_results: int = 10, sort: str = "relevance") -> list[str]:
        """Search method for PubMed API articles.

        Args:
            query: PubMed search query.
            max_results: Max number of articles IDs to return.
            sort: Sorting method for search results.
        
        Returns:
            List of PubMed article IDs (PMIDS).
        """
        endpoint  = "esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax" : max_results,
            "sort": sort
        }
        response = self.get(endpoint=endpoint, params=params)
        data = response.json()
        pmids = data["esearchresult"]["idlist"]
        return pmids

    def efetch(self, pmids: list[str]) -> str:
        """Fetch method for PubMed API articles.

        Args:
            pmids: List of PubMed article IDs (PMIDS).

        Returns:
            XML response containing the requested articles.
        """
        endpoint  = "efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "rettype" : "abstract",
        }
        response = self.get(endpoint=endpoint, params=params)
        return response.text


        

            

