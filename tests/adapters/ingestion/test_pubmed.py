import time
import requests
from requests.adapters import HTTPAdapter
from unittest.mock import Mock
import pytest
from src.app.config.settings import PubMedSettings
from src.app.adapters.ingestion.pubmed import PubMedRequestTransport
from src.app.exceptions.ingestion import PubMedTimeOutError, PubMedTransportError, PubMedHTTPError


def test_transport():
    config = PubMedSettings()
    transport = PubMedRequestTransport(config)

    assert transport.config.pubmed_api_key == None
    assert transport.config.base_url == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    assert transport.config.max_retries == 2
    assert transport.config.backoff_factor == 1.0
    assert transport.config.request_interval == 0.1

def test_create_session():
    config = PubMedSettings()
    transport = PubMedRequestTransport(config)
    session = transport.create_session()

    assert isinstance(session.adapters["https://"], HTTPAdapter)
    assert isinstance(session.adapters["http://"], HTTPAdapter)
    assert transport.config.backoff_factor == 1.0
    assert transport.config.max_retries == 2

def test_rate_limit(monkeypatch):
    config = PubMedSettings()
    transport = PubMedRequestTransport(config)
    transport.last_request_time = 10

    mock_sleep = Mock()
    monkeypatch.setattr(time, "sleep", mock_sleep)
    monkeypatch.setattr(time, "monotonic", Mock(return_value=10.05))

    transport.rate_limit()

    mock_sleep.assert_called_once()
    assert transport.last_request_time == 10.05

def test_get(monkeypatch):
    config = PubMedSettings(pubmed_api_key="test_key")
    transport = PubMedRequestTransport(config)

    mock_response = Mock(status_code=200)
    mock_get = Mock(return_value=mock_response)

    monkeypatch.setattr(transport, "rate_limit", Mock())
    monkeypatch.setattr(transport.session, "get", mock_get)

    response = transport.get("esearch.fcgi", {"db": "pubmed"})

    assert response == mock_response
    mock_get.assert_called_once_with(
        f"{config.base_url}/esearch.fcgi",
        params={"db": "pubmed", "api_key": "test_key"},
        timeout=10,
    )

def test_get_timeout(monkeypatch):
    transport = PubMedRequestTransport(PubMedSettings())

    monkeypatch.setattr(transport, "rate_limit", Mock())
    monkeypatch.setattr(
        transport.session,
        "get",
        Mock(side_effect=requests.Timeout("Timeout")),
    )

    with pytest.raises(PubMedTimeOutError):
        transport.get("esearch.fcgi", {"db": "pubmed"})

def test_get_transport_error(monkeypatch):
    transport = PubMedRequestTransport(PubMedSettings())

    monkeypatch.setattr(transport, "rate_limit", Mock())
    monkeypatch.setattr(
        transport.session,
        "get",
        Mock(side_effect=requests.ConnectionError("Connection failed")),
    )

    with pytest.raises(PubMedTransportError):
        transport.get("esearch.fcgi", {"db": "pubmed"})

def test_get_http_error(monkeypatch):
    transport = PubMedRequestTransport(PubMedSettings())

    mock_response = Mock(status_code=404)

    monkeypatch.setattr(transport, "rate_limit", Mock())
    monkeypatch.setattr(
        transport.session,
        "get",
        Mock(return_value=mock_response),
    )

    with pytest.raises(PubMedHTTPError):
        transport.get("esearch.fcgi", {"db": "pubmed"})

def test_esearch(monkeypatch):
    transport = PubMedRequestTransport(PubMedSettings())

    mock_response = Mock()
    mock_response.json.return_value = {
        "esearchresult": {
            "idlist": ["12345", "67890"]
        }
    }

    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr(transport, "get", mock_get)

    result = transport.esearch("cancer", max_results=2)

    assert result == ["12345", "67890"]

    mock_get.assert_called_once_with(
        endpoint="esearch.fcgi",
        params={
            "db": "pubmed",
            "term": "cancer",
            "retmode": "json",
            "retmax": 2,
            "sort": "relevance",
        },
    )

def test_efetch(monkeypatch):
    transport = PubMedRequestTransport(PubMedSettings())

    mock_response = Mock()
    mock_response.text = "<xml>articles</xml>"

    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr(transport, "get", mock_get)

    result = transport.efetch(["12345", "67890"])

    assert result == "<xml>articles</xml>"

    mock_get.assert_called_once_with(
        endpoint="efetch.fcgi",
        params={
            "db": "pubmed",
            "id": "12345,67890",
            "retmode": "xml",
            "rettype": "abstract",
        },
    )
