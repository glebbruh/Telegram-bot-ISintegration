#Авторизация
import os

import httpx
from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from email_validator import EmailNotValidError, validate_email

router = Router()

class AuthStates(StatesGroup):
    waiting_for_email = State()

async def send_auth_to_backend(email: str, telegram_id: int) -> bool:
    backend_url = os.getenv("BACKEND_AUTH_URL", "").strip()
    if not backend_url:
        raise RuntimeError("BACKEND_AUTH_URL is not set")
    payload = {
        "email": email,
        "telegram_id": telegram_id
    }
    timeout = httpx.Timeout(15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(backend_url, json=payload)
        response.raise_for_status()
        data = response.json()
    return bool(data.get("success"))

#обработка старта
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(AuthStates.waiting_for_email)
    await message.answer(
        "Для входа в бот введите ваш email"
    )

#обработка ввода email
@router.message(StateFilter(AuthStates.waiting_for_email))
async def process_email(message: Message, state: FSMContext):
    raw_email = (message.text or "").strip()
    telegram_id = message.from_user.id
    try:
        valid = validate_email(raw_email, check_deliverability=False)
        email = valid.normalized
    except EmailNotValidError:
        await message.answer(
            "Некорректный email. Пожалуйста, введите email ещё раз."
        )
        return
    try:
        is_authorized = await send_auth_to_backend(
            email=email,
            telegram_id=telegram_id
        )
    except httpx.HTTPStatusError:
        await message.answer(
            "Сервер авторизации вернул ошибку. Попробуйте позже."
        )
        return
    except httpx.RequestError:
        await message.answer(
            "Не удалось связаться с сервером авторизации. Попробуйте позже."
        )
        return
    except Exception:
        await message.answer(
            "Произошла внутренняя ошибка. Попробуйте позже."
        )
        return
    if is_authorized:
        await state.clear()
        await message.answer(
            "Авторизация прошла успешно."
        )
    else:
        await message.answer(
            "Пользователь не найден или не прошёл проверку. Введите email ещё раз."
        )