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
    CHECKOFFICE_USERS_PATH: str = os.getenv(
        "CHECKOFFICE_USERS_PATH"
    )
    CHECKOFFICE_PER_PAGE: int = int(
        os.getenv("CHECKOFFICE_PER_PAGE")
    )


settings = Settings()