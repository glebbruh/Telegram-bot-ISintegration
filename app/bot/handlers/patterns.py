#Работа с шаблонами чек-листов
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.filters.checks_common import save_filter
from bot.handlers.common import require_user_id, send_new_filters_message
from bot.keyboards.callbacks import ChecksMenuCb, PatternChoiceCb
from bot.keyboards.checks import patterns_results_keyboard
from bot.services.connect_with_backend import fetch_patterns_from_backend

router = Router()

class PatternSearchStates(StatesGroup):
    waiting_pattern_query = State()

@router.callback_query(ChecksMenuCb.filter(F.action == "pattern"))
async def open_pattern_search(callback: CallbackQuery, state: FSMContext):
    user_id = await require_user_id(callback, state)
    if user_id is None:
        return
    try:
        patterns = await fetch_patterns_from_backend(user_id)
    except Exception as e:
        await callback.answer(f"Не удалось получить шаблоны: {e}", show_alert=True)
        return
    await state.update_data(available_patterns=patterns)
    await state.set_state(PatternSearchStates.waiting_pattern_query)
    try:
        await callback.message.delete()
    except Exception:
        pass
    prompt = await callback.message.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Введите часть названия шаблона чек-листа."
    )
    await state.update_data(
        pattern_prompt_message_id=prompt.message_id
    )
    await callback.answer()

@router.message(StateFilter(PatternSearchStates.waiting_pattern_query))
async def process_pattern_search(message: Message, state: FSMContext):
    query = (message.text or "").strip().lower()
    if not query:
        await message.answer("Введите хотя бы один символ для поиска.")
        return
    data = await state.get_data()
    available_patterns = data.get("available_patterns", [])
    results = [
        item for item in available_patterns
        if query in item["name"].lower()
    ][:10]
    prompt_message_id = data.get("pattern_prompt_message_id")
    if prompt_message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=prompt_message_id
            )
        except Exception:
            pass
    try:
        await message.delete()
    except Exception:
        pass
    if not results:
        msg = await message.bot.send_message(
            chat_id=message.chat.id,
            text="Ничего не найдено. Введите другой запрос."
        )
        await state.update_data(pattern_prompt_message_id=msg.message_id)
        return
    results_message = await message.bot.send_message(
        chat_id=message.chat.id,
        text="Найдены шаблоны. Выберите один из списка:",
        reply_markup=patterns_results_keyboard(results)
    )
    await state.update_data(
        pattern_results_message_id=results_message.message_id
    )

@router.callback_query(PatternChoiceCb.filter())
async def process_pattern_choice(
    callback: CallbackQuery,
    callback_data: PatternChoiceCb,
    state: FSMContext,
):
    pattern_id = callback_data.pattern_id
    data = await state.get_data()
    available_patterns = data.get("available_patterns", [])
    pattern = next(
        (item for item in available_patterns if item["id"] == pattern_id),
        None
    )
    if not pattern:
        await callback.answer("Шаблон не найден", show_alert=True)
        return
    await save_filter(
        state,
        "pattern",
        {
            "id": pattern["id"],
            "name": pattern["name"],
        }
    )
    try:
        await callback.message.delete()
    except Exception:
        pass
    await state.set_state(None)
    await callback.answer("Шаблон сохранён")
    await send_new_filters_message(
        chat_id=callback.message.chat.id,
        bot=callback.bot,
        state=state
    )