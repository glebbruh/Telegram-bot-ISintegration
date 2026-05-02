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

#TEST WITHOUT BACKEND
from bot.keyboards.menu import main_sections_keyboard

# @router.message(CommandStart())
# async def cmd_start(message: Message, state: FSMContext):
#     await message.answer(
#         "Выберите раздел:",
#         reply_markup=main_sections_keyboard()
#     )

def _backend_base_url() -> str:
    base_url = os.getenv("BACKEND_AUTH_URL", "").strip()
    if not base_url:
        raise RuntimeError("BACKEND_AUTH_URL is not set")
    return base_url.rstrip("/")

async def send_auth_to_backend(email: str, telegram_id: int) -> dict:
    url = f"{_backend_base_url()}/auth/login"
    payload = {
        "email": email,
        "telegram_id": telegram_id
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
    return {
        "success": bool(data.get("success")),
        "user_id": data.get("user_id"),
    }

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
        auth_result = await send_auth_to_backend(
            email=email,
            telegram_id=telegram_id
        )
    except httpx.HTTPStatusError as e:
        await message.answer(
            f"Сервер авторизации вернул ошибку: HTTP {e.response.status_code}\n{e.response.text}"
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
    if auth_result["success"]:
        user_id = auth_result.get("user_id")
        if user_id is None:
            await message.answer(
                "Бекэнд не вернул id пользователя. Попробуйте позже."
            )
            return
        await state.update_data(user_id=user_id)
        await state.set_state(None)
        await message.answer(
            "Вы успешно вошли в программу.",
            reply_markup=main_sections_keyboard()
        )
    else:
        await message.answer(
            "Пользователь не найден или не прошёл проверку. Введите email ещё раз."
        )