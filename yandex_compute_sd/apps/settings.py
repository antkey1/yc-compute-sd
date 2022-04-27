from pydantic import BaseSettings


class Settings(BaseSettings):
    folder_id: str
    service_account_id: str
    key_id: str
    private_key: str

    class Config:
        env_prefix = 'yc_compute_sd_'
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
