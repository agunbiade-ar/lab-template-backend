from pydantic_settings import BaseSettings, SettingsConfigDict
# from sqlalchemy.engine import URL
from urllib.parse import quote_plus

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    CONFIRMATION_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def DATABASE_URL(self):
        # print(f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")
        return f"postgresql+asyncpg://{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        # return URL.create(
        #     drivername="postgresql+asyncpg",
        #     username=self.DB_USER,
        #     password=self.DB_PASSWORD,  # No need to encode, SQLAlchemy handles it
        #     host=self.DB_HOST,
        #     port=int(self.DB_PORT),
        #     database=self.DB_NAME
        # )

Config = Settings()