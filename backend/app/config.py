from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_base_url: str | None = None
    mock_llm: bool = False
    llm_model: str = "gpt-4o-mini"
    paypal_client_id: str
    paypal_client_secret: str
    paypal_mode: str = "sandbox"
    paypal_webhook_id: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    database_url: str = "sqlite:///./data/app.db"
    secret_key: str
    frontend_url: str
    backend_url: str
    enable_scheduler: bool = False


settings = Settings()  # type: ignore[call-arg]