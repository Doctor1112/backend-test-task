from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    DB_HOST: str
    DB_PASS: str
    DB_NAME: str
    DB_USER: str
    DB_PORT: str
    DB_TEST_HOST: str
    DB_TEST_PASS: str
    DB_TEST_NAME: str
    DB_TEST_USER: str
    DB_TEST_PORT: str

    model_config = SettingsConfigDict(env_file=".env")
    

settings = Settings()