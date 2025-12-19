from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Identity
    app_name: str = "fastapi-mongo-k8s"
    environment: str = "development"
    location: str = "local"
    
    # Logging
    debug: bool = False
    
    # MongoDB - Single source of truth
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "fastapi_db"
    
    # Connection pooling
    mongodb_max_pool_size: int = 100
    mongodb_min_pool_size: int = 10
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

settings = Settings()