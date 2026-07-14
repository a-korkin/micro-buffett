from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    FILENAME: str = ""
    DIR: str = ""
    ISS_HOST: str = ""
    BASE_URL: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    DB_URL: str = ""
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 465
    SENDER_EMAIL: str = ""
    SENDER_PASSWORD: str = ""
    RECIPIENT_EMAIL: str = ""


app_settings = AppSettings()
