from pydantic_settings import BaseSettings, SettingsConfigDict

class PubMedSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    pubmed_api_key: str | None = None
    base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    max_retries: int = 2
    backoff_factor: float = 1.0
    request_interval: float = 0.1
