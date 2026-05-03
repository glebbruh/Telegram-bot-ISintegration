from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.filters.checks_common import build_filters_text, get_filters
from bot.filters.tasks_common import build_tasks_filters_text, get_task_filters
from bot.keyboards.checks import checks_filters_keyboard
from bot.keyboards.tasks import tasks_filters_keyboard
from bot.services.auth_help import AuthStates

async def get_current_user_id(state: FSMContext) -> int | None:
    data = await state.get_data()
    return data.get("user_id")

async def require_user_id(callback: CallbackQuery, state: FSMContext) -> int | None:
    user_id = await get_current_user_id(state)
    if user_id is None:
        await state.set_state(AuthStates.waiting_for_email)
        await callback.answer()
        await callback.message.answer(
            "Сессия сбросилась или вы ещё не авторизованы.\n"
            "Введите ваш email для входа."
        )
        return None
    return user_id

async def send_new_filters_message(chat_id: int, bot, state: FSMContext):
    filters = await get_filters(state)
    text = build_filters_text(filters)
    markup = checks_filters_keyboard(filters)
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=markup
    )

async def show_filters_message(target: Message | CallbackQuery, state: FSMContext):
    filters = await get_filters(state)
    text = build_filters_text(filters)
    markup = checks_filters_keyboard(filters)

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=markup)
    else:
        await target.answer(text, reply_markup=markup)

async def show_tasks_filters_message(target: Message | CallbackQuery, state: FSMContext):
    filters = await get_task_filters(state)
    text = build_tasks_filters_text(filters)
    markup = tasks_filters_keyboard(filters)
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=markup)
    else:
        await target.answer(text, reply_markup=markup)

async def toggle_mutually_exclusive_flag(
    state: FSMContext,
    get_filters_func,
    save_filter_func,
    remove_filter_func,
    current_key: str,
    opposite_key: str,
) -> bool:
    filters = await get_filters_func(state)
    current_value = filters.get(current_key, {}).get("value", False)
    if current_value:
        await remove_filter_func(state, current_key)
        return False
    if filters.get(opposite_key, {}).get("value", False):
        await remove_filter_func(state, opposite_key)
    await save_filter_func(
        state,
        current_key,
        {
            "value": True,
        }
    )
    return True