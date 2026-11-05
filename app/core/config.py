from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application settings
    app_name: str = "ShopEase Standalone Authentication Service"
    app_env: str = "development"

    # MySQL connection settings
    db_host: str
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: SecretStr

    # JWT security settings
    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Read values from the project's .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Create one reusable settings object
settings = Settings()
