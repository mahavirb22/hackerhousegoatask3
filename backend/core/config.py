from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine project root (.env location)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Monorepo Service"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment credentials (with defaults/fallbacks)
    SERPAPI_KEY: str = ""
    WEB3_PROVIDER_URL: str = ""
    PRIVATE_KEY: str = ""
    CONTRACT_ADDRESS: str = ""
    
    # IPFS Credentials
    IPFS_HOST: str = "ipfs.infura.io"
    IPFS_PORT: int = 5001
    IPFS_PROJECT_ID: str = ""
    IPFS_PROJECT_SECRET: str = ""
    IPFS_GATEWAY_URL: str = "https://ipfs.io/ipfs/"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
