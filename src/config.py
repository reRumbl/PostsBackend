import os
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_file_path():
    '''Function for find .env file'''
    for root, _, files in os.walk('.'):
        if '.env' in files:
            return os.path.join(root, '.env')


class Settings(BaseSettings):
    '''App settings class'''
    # Python
    PYTHONPATH: str
    
    # App
    APP_HOST: str
    APP_PORT: int
    
    # Logging
    LOG_LEVEL: str
    LOG_INTO_CONSOLE: bool
    LOG_INTO_FILES: bool
    
    # Database
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int
    DB_ECHO: bool
    
    # Test database
    DB_USER_TEST: str
    DB_PASS_TEST: str
    DB_HOST_TEST: str
    DB_PORT_TEST: int
    DB_NAME_TEST: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGHORITM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int
    
    # Redis
    REDIS_HOST: str
    
    # S3
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_ENDPOINT_URL: str
    S3_BUCKET_NAME: str
    
    @property
    def asyncpg_url(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    @property
    def test_asyncpg_url(self):
        return f'postgresql+asyncpg://{self.DB_USER_TEST}:{self.DB_PASS_TEST}@{self.DB_HOST_TEST}:{self.DB_PORT_TEST}/{self.DB_NAME_TEST}'

    model_config = SettingsConfigDict(env_file=get_env_file_path())


settings = Settings()
