import httpx

from app.core.config import settings
from app.schemas.checkoffice import CheckOfficeUser


class CheckOfficeService:
    @staticmethod
    async def request(
        method: str,
        path: str,
        params: dict | None = None,
    ) -> dict | list | None:
        url = f"{settings.CHECKOFFICE_BASE_URL.rstrip('/')}{path}"

        headers = {
            "API-Key": settings.CHECKOFFICE_API_KEY,
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
            )

        response.raise_for_status()

        if not response.content:
            return None

        return response.json()

    @classmethod
    async def get_users_page(cls, page: int) -> dict:
        data = await cls.request(
            method="GET",
            path=settings.CHECKOFFICE_USERS_PATH,
            params={
                "page": page,
                "per_page": settings.CHECKOFFICE_PER_PAGE,
            },
        )

        if not isinstance(data, dict):
            raise ValueError("Некорректный ответ от CheckOffice")

        return data

    @classmethod
    def extract_user(cls, raw_user: dict) -> CheckOfficeUser | None:
        user_id = raw_user.get("id")
        user_email = raw_user.get("email")

        if user_id is None or user_email is None:
            return None

        try:
            return CheckOfficeUser(
                id=user_id,
                email=user_email,
            )
        except Exception:
            return None

    @classmethod
    async def find_user_by_email(cls, email: str) -> CheckOfficeUser | None:
        target_email = email.lower().strip()
        page = 1

        while True:
            payload = await cls.get_users_page(page)

            users = payload.get("data", [])
            current_page = payload.get("current_page", page)
            last_page = payload.get("last_page", page)

            for raw_user in users:
                if not isinstance(raw_user, dict):
                    continue

                user = cls.extract_user(raw_user)
                if user is None:
                    continue

                if user.email.lower().strip() == target_email:
                    return user

            if not users or current_page >= last_page:
                break

            page += 1

        return None