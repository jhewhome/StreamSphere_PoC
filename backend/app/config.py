from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "streamsphere"
    postgres_user: str = "streamsphere"
    postgres_password: str = "streamsphere"

    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db: str = "streamsphere"

    jwt_secret: str = "change-me-in-production-streamsphere-poc"
    jwt_expire_minutes: int = 480
    jwt_algorithm: str = "HS256"

    tmdb_api_key: str = ""
    tmdb_base_url: str = "https://api.themoviedb.org/3"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"host={self.postgres_host} port={self.postgres_port} "
            f"dbname={self.postgres_db} user={self.postgres_user} "
            f"password={self.postgres_password}"
        )

    @property
    def mongo_uri(self) -> str:
        return f"mongodb://{self.mongo_host}:{self.mongo_port}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
