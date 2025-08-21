from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "dev"

    class Config:
        env_file = "/app/.env"  # docker-compose의 env_file이 루트에 있을 때 컨테이너 내 경로 기준
        extra = "ignore"

settings = Settings()