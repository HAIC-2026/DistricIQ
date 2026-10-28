from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    app_name: str = "DistrictIQ Hawaii"
    app_env: str = "development"
    debug: bool = False
    database_url: SecretStr = SecretStr("postgresql+psycopg://districtiq@localhost:5432/districtiq")
    openai_api_key: SecretStr = SecretStr("")
    openai_model: str = "gpt-4.1"
    census_api_key: SecretStr = SecretStr("")
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    house_district_layer_url: str = "https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/33"
    senate_district_layer_url: str = "https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/34"
    geoportal_base_url: str = "https://geoportal.hawaii.gov"
    geoportal_search_api: str = "https://geoportal.hawaii.gov/api/search/v1"
    geoportal_dcat_url: str = "https://geoportal.hawaii.gov/api/feed/dcat-us/1.1.json"
    cache_dir: Path = ROOT / "data/raw/cache"
    cache_ttl_seconds: int = 86400
    max_response_bytes: int = 24_000_000


@lru_cache
def get_settings() -> Settings:
    return Settings()
