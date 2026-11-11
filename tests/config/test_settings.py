from src.app.config.settings import PubMedSettings

def test_pubmed_settings():
    settings = PubMedSettings(
        base_url = "https://eutils.ncbi.nlm.nih.gov/test/test_v1",
        max_retries = 5,
        backoff_factor = 5.0,
        request_interval = 7.0
    )

    assert settings.base_url == "https://eutils.ncbi.nlm.nih.gov/test/test_v1"
    assert settings.max_retries == 5
    assert settings.backoff_factor == 5.0
    assert settings.request_interval == 7.0
