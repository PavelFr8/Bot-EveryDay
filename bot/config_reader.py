from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    bot_token: SecretStr
    host_url: SecretStr
    api_url: SecretStr
    postgres_db: SecretStr
    postgres_user: SecretStr
    postgres_port: SecretStr
    postgres_password: SecretStr
    postgres_host: SecretStr

    @property
    def async_postgresql_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user.get_secret_value()}:"
            f"{self.postgres_password.get_secret_value()}@"
            f"{self.postgres_host.get_secret_value()}:"
            f"{self.postgres_port.get_secret_value()}/"
            f"{self.postgres_db.get_secret_value()}"
        )

    @property
    def sync_postgresql_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user.get_secret_value()}:"
            f"{self.postgres_password.get_secret_value()}@"
            f"{self.postgres_host.get_secret_value()}:"
            f"{self.postgres_port.get_secret_value()}/"
            f"{self.postgres_db.get_secret_value()}"
        )


config = Settings()
