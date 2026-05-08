import httpx
from fastapi import APIRouter, BackgroundTasks

from app.core.config import settings
from app.schemas.webhook_schema import WebhookModel, WebhookEvent, WebhookResponse
from app.services.db_service import get_chat_id

router = APIRouter(tags=["webhook"])


async def send_to_bot(webhook: WebhookResponse):
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(settings.BOT_WEBHOOK_URL,
                                     json=webhook.model_dump(mode="json"))

    if response.status_code > 200:
        print(f"Ошибка при отправке вебхука в бот: {response.status_code} {response.text}")



@router.post('/checkoffice')
async def get_webhook(payload: WebhookModel,
                      background_task: BackgroundTasks):

    data = payload.data
    event = payload.event
    assignee = data.get('assignee') or {}
    creator = data.get('creator') or {}

    assignee_id = assignee.get('id')
    creator_id = creator.get('id')

    assignee_chat_id = await get_chat_id(assignee_id) if assignee_id else None
    creator_chat_id = await get_chat_id(creator_id) if creator_id else None

    if assignee_chat_id is not None:
        if event == WebhookEvent.task_create or event == WebhookEvent.task_changeStatus:
            response = WebhookResponse(chat_id=assignee_chat_id,
                                       event_type=event,
                                       name=data.get('title'),
                                       status=data.get('status'),
                                       assignee=True,
                                       creator=False)
            background_task.add_task(send_to_bot, response)
        elif event == WebhookEvent.inspection_create or event == WebhookEvent.inspection_changeStatus:
            response = WebhookResponse(chat_id=assignee_chat_id,
                                       event_type=event,
                                       name=data.get('place').get('name'),
                                       status=data.get('status'),
                                       assignee=True,
                                       creator=False)
            background_task.add_task(send_to_bot, response)

    if creator_chat_id is not None:
        if event == WebhookEvent.task_create or event == WebhookEvent.task_changeStatus:
            response = WebhookResponse(chat_id=creator_chat_id,
                                       event_type=event,
                                       name=data.get('title'),
                                       status=data.get('status'),
                                       assignee=False,
                                       creator=True)
            background_task.add_task(send_to_bot, response)
        elif event == WebhookEvent.inspection_create or event == WebhookEvent.inspection_changeStatus:
            response = WebhookResponse(chat_id=creator_chat_id,
                                       event_type=event,
                                       name=data.get('place').get('name'),
                                       status=data.get('status'),
                                       assignee=False,
                                       creator=True)
            background_task.add_task(send_to_bot, response)



    return {"status": "success"}
