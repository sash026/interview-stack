from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Interview Stack"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    DATABASE_URL: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/interview_stack"
    )

    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"
    AWS_STORAGE_BUCKET_NAME: str = "interview-stack-audio"
    AWS_S3_ENDPOINT_URL: str | None = None

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Selects the TranscriptionProvider implementation (see
    # app/services/transcription_service.py). "mock" is the only
    # implementation today; add new ones and extend the factory to support
    # real providers (e.g. "openai_whisper").
    TRANSCRIPTION_PROVIDER: str = "mock"

    # Selects the AIProvider implementation (see app/services/ai_service.py).
    # "mock" needs no credentials; "openai" requires OPENAI_API_KEY. Add new
    # providers (Anthropic, Gemini, ...) by implementing AIProvider and
    # registering them in ai_service._PROVIDERS.
    AI_PROVIDER: str = "mock"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-5.5"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"


settings = Settings()
