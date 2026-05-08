import os

from dotenv import load_dotenv

load_dotenv()

class Settings:
    CHECKOFFICE_BASE_URL: str = os.getenv(
        "CHECKOFFICE_BASE_URL"
    )
    CHECKOFFICE_API_KEY: str = os.getenv(
        "CHECKOFFICE_API_KEY"
    )
    CHECKOFFICE_PER_PAGE: int = int(
        os.getenv("CHECKOFFICE_PER_PAGE")
    )


    CHECKOFFICE_USERS_PATH: str = "/publicapi/v1/users"
    CHECKOFFICE_PATTERNS_PATH: str = "/publicapi/v1/patterns"
    CHECKOFFICE_TASKS_PATH: str = "/publicapi/v1/tasks"
    CHECKOFFICE_INSPECTIONS_PATH: str = "/publicapi/v1/inspections"

    BOT_WEBHOOK_URL: str = "http://127.0.0.1:8081/webhook/events"


settings = Settings()