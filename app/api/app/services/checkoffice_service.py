import datetime

import httpx

from app.core.config import settings
from app.schemas.checkoffice import (
    CheckOfficeUser,
    Pattern,
    CheckOfficeTask,
    CheckOfficeInspection,
)
from app.schemas.inspection_schema import InspectionStatus




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



    #### user ####

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
                email=user_email
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

                if str(user.email).lower().strip() == target_email:
                    return user

            if not users or current_page >= last_page:
                break

            page += 1

        return None



    #### patterns ####

    @classmethod
    def extract_pattern(cls, raw_pattern: dict) -> Pattern | None:
        pattern_id = raw_pattern.get("id")
        pattern_name = raw_pattern.get("name")

        if pattern_id is None or pattern_name is None:
            return None

        try:
            return Pattern(id=pattern_id, name=pattern_name)
        except Exception:
            return None

    @classmethod
    async def get_patterns_page(cls, page: int) -> dict:
        data = await cls.request(method="GET",
                    path=settings.CHECKOFFICE_PATTERNS_PATH,
                    params={
                        "page": page,
                        "per_page": settings.CHECKOFFICE_PER_PAGE,
                    })
        if not isinstance(data, dict):
            raise ValueError("Некорректный ответ от CheckOffice")

        return data

    @classmethod
    async def get_patterns(cls) -> list[Pattern]:
        page = 1

        return_pattern_list = []

        while True:
            payload = await cls.get_patterns_page(page)
            patterns = payload.get("data", [])
            current_page = payload.get("current_page", page)
            last_page = payload.get("last_page", page)


            for raw_pattern in patterns:
                if not isinstance(raw_pattern, dict):
                    continue

                pattern = cls.extract_pattern(raw_pattern)
                if pattern is None:
                    continue

                return_pattern_list.append(pattern)

            if current_page >= last_page:
                break

            page += 1

        return return_pattern_list




    #### tasks ####

    @classmethod
    def extract_task(cls, raw_task: dict) -> CheckOfficeTask | None:
        task_title = raw_task.get("title")
        task_status = raw_task.get("status")
        task_priority = raw_task.get("priority")
        task_expire_at = raw_task.get("expire_at")

        if task_title is None or task_status is None or task_priority is None or task_expire_at is None:
            return None

        try:
            return CheckOfficeTask(title=task_title,
                                   status=task_status,
                                   priority=task_priority,
                                   expire_at=task_expire_at,
                                   assignee=raw_task.get("assignee"),
                                   creator=raw_task.get("creator")
                                   )
        except Exception:
            return None

    @classmethod
    async def get_task_page(cls, page: int, params: dict) -> dict:
        request_params = {
            **params,
            "page": page,
            "per_page": settings.CHECKOFFICE_PER_PAGE,
        }
        data = await cls.request(method="GET",
                                 path=settings.CHECKOFFICE_TASKS_PATH,
                                 params=request_params,
                                 )
        if not isinstance(data, dict):
            raise ValueError("Некорректный ответ от CheckOffice")

        return data

    @classmethod
    async def get_tasks(cls, params: dict) -> list[CheckOfficeTask]:
        page = 1
        return_task_list = []

        allowed_filters = [
            "t:deadline_at_from",
            "t:deadline_at_to",
        ]
        query_params = {k: v for k, v in params.items() if k in allowed_filters and v is not None}
        priority = params.get("priority")
        user_id = params.get("user_id")
        show_my = params.get("show_my", False)
        made_by_me = params.get("made_by_me", False)

        if show_my == True and user_id is not None :
            query_params["t:assignees[]"] = user_id
        elif made_by_me == True and user_id is not None :
            query_params["t:creators[]"] = user_id

        while True:
            payload = await cls.get_task_page(page, query_params)
            tasks = payload.get("data", [])
            current_page = payload.get("current_page", page)
            last_page = payload.get("last_page", page)

            for raw_task in tasks:
                if not isinstance(raw_task, dict):
                    continue

                task = cls.extract_task(raw_task)

                if task is None:
                    continue

                if priority is None:
                    return_task_list.append(task)
                elif task.priority == priority:
                    return_task_list.append(task)



            if current_page >= last_page:
                break

            page += 1

        return return_task_list


    @classmethod
    async def get_tasks_today_summary(cls) -> dict:
        today = datetime.date.today()

        query_params = {
            "t:deadline_at_from": f"{today.isoformat()}T00:00:00",
            "t:deadline_at_to": f"{today.isoformat()}T23:59:59",
        }

        page = 1

        summary = {
            "created": 0,
            "process": 0,
            "revise": 0,
            "review": 0,
            "validation": 0,
            "completed": 0,
            "archived": 0,
            "manual_review": 0,
            "cancelled": 0,
        }

        while True:
            payload = await cls.get_task_page(page, query_params)

            tasks = payload.get("data", [])
            current_page = payload.get("current_page", page)
            last_page = payload.get("last_page", page)

            for raw_task in tasks:
                if not isinstance(raw_task, dict):
                    continue

                task = cls.extract_task(raw_task)

                if task is None:
                    continue

                task_status = (
                    task.status.value
                    if hasattr(task.status, "value")
                    else task.status
                )

                if task_status in summary:
                    summary[task_status] += 1

            if not tasks or current_page >= last_page:
                break

            page += 1

        return summary




    #### inspections ####

    @classmethod
    def extract_inspection(cls, raw_inspection: dict) -> CheckOfficeInspection | None:
        inspection_status = raw_inspection.get("status")

        if inspection_status is None:
            return None

        try:
            return CheckOfficeInspection(
                status=inspection_status,
                date=raw_inspection.get("date"),
                deadline_at=raw_inspection.get("deadline_at"),
                finished_at=raw_inspection.get("finished_at"),
                place=raw_inspection.get("place"),
                pattern=raw_inspection.get("pattern"),
                assignee=raw_inspection.get("assignee"),
                creator=raw_inspection.get("creator"),
            )
        except Exception:
            return None

    @classmethod
    async def get_inspection_page(cls, page: int, params: dict) -> dict:
        request_params = {
            **params,
            "page": page,
            "per_page": settings.CHECKOFFICE_PER_PAGE,
        }

        data = await cls.request(
            method="GET",
            path=settings.CHECKOFFICE_INSPECTIONS_PATH,
            params=request_params,
        )

        if not isinstance(data, dict):
            raise ValueError("Некорректный ответ от CheckOffice")

        return data


    @staticmethod
    def is_inspection_overdue(inspection: CheckOfficeInspection) -> bool:
        if inspection.deadline_at is None:
            return False

        if inspection.status == InspectionStatus.completed:
            return False

        return inspection.deadline_at < datetime.datetime.now()

    @staticmethod
    def is_inspection_finished_in_period(
        inspection: CheckOfficeInspection,
        finished_at_from: str | None,
        finished_at_to: str | None,
    ) -> bool:
        if finished_at_from is None and finished_at_to is None:
            return True

        if inspection.finished_at is None:
            return False

        from_dt = None
        to_dt = None

        if finished_at_from is not None:
            from_dt = datetime.datetime.fromisoformat(finished_at_from)

        if finished_at_to is not None:
            to_dt = datetime.datetime.fromisoformat(finished_at_to)

        if from_dt is not None and inspection.finished_at < from_dt:
            return False

        if to_dt is not None and inspection.finished_at > to_dt:
            return False

        return True

    @classmethod
    async def get_inspections(cls, params: dict) -> list[CheckOfficeInspection]:
        page = 1
        result = []

        query_params = {
            key: value
            for key, value in params.items()
            if key in ["i:date_from", "i:date_to"] and value is not None
        }

        user_id = params.get("user_id")
        show_my = params.get("show_my", True)
        made_by_me = params.get("made_by_me", False)

        status_filter = params.get("status")
        pattern_id = params.get("pattern_id")
        overdue = params.get("overdue")

        finished_at_from = params.get("finished_at_from")
        finished_at_to = params.get("finished_at_to")

        if show_my and user_id is not None:
            query_params["i:assignees[]"] = [user_id]

        if made_by_me and user_id is not None:
            query_params["i:creators[]"] = [user_id]

        if status_filter is not None:
            query_params["i:statuses[]"] = [status_filter]

        if pattern_id is not None:
            query_params["i:patterns[]"] = [pattern_id]

        while True:
            payload = await cls.get_inspection_page(page, query_params)

            inspections = payload.get("data", [])
            current_page = payload.get("current_page", page)
            last_page = payload.get("last_page", page)

            for raw_inspection in inspections:
                if not isinstance(raw_inspection, dict):
                    continue

                inspection = cls.extract_inspection(raw_inspection)

                if inspection is None:
                    continue

                if not cls.is_inspection_finished_in_period(
                    inspection=inspection,
                    finished_at_from=finished_at_from,
                    finished_at_to=finished_at_to,
                ):
                    continue

                if overdue is not None and cls.is_inspection_overdue(inspection) != overdue:
                    continue

                result.append(inspection)

            if not inspections or current_page >= last_page:
                break

            page += 1

        return result


    @classmethod
    async def get_inspections_today_summary(cls) -> dict:
        today = datetime.date.today()

        query_params = {
            "i:date_from": f"{today.isoformat()}T00:00:00",
            "i:date_to": f"{today.isoformat()}T23:59:59",
        }

        page = 1

        summary = {
            "created": 0,
            "process": 0,
            "verification": 0,
            "completed": 0,
        }

        while True:
            payload = await cls.get_inspection_page(page, query_params)

            inspections = payload.get("data", [])
            current_page = payload.get("current_page", page)
            last_page = payload.get("last_page", page)

            for raw_inspection in inspections:
                if not isinstance(raw_inspection, dict):
                    continue

                inspection = cls.extract_inspection(raw_inspection)

                if inspection is None:
                    continue

                inspection_status = (
                    inspection.status.value
                    if hasattr(inspection.status, "value")
                    else inspection.status
                )

                if inspection_status in summary:
                    summary[inspection_status] += 1

            if not inspections or current_page >= last_page:
                break

            page += 1

        return summary




