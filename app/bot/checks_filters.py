import os
import httpx
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from menu import (
    ChecksMenuCb,
    OverdueChoiceCb,
    StatusChoiceCb,
    PatternChoiceCb,
    TasksMenuCb,
    TaskPriorityChoiceCb,
    checks_filters_keyboard,
    overdue_keyboard,
    status_keyboard,
    task_priority_keyboard,
    tasks_filters_keyboard,
    patterns_results_keyboard,
)
from tasks_common import (
    build_tasks_filters_text,
    clear_task_filters,
    get_task_filters,
    remove_task_filter,
    save_task_filter,
)
from connect_with_backend import(
    fetch_patterns_from_backend,
    send_checks_filters_to_backend,
    send_tasks_filters_to_backend,
)
from result_formatters import (
    build_checks_status_legend,
    format_checks_response,
    format_tasks_response,
)
from bot_calendar import open_range_calendar
from checks_common import build_filters_text, get_filters, remove_filter, save_filter

router = Router()

class PatternSearchStates(StatesGroup):
    waiting_pattern_query = State()


STATUS_LABELS = {
    "created": "Назначено",
    "process": "В работе",
    "completed": "Завершено",
    "verification": "Валидация",
}

TASK_PRIORITY_LABELS = {
    "none": "Без приоритета",
    "low": "Низкий",
    "medium": "Средний",
    "high": "Высокий",
}

async def get_current_user_id(state: FSMContext) -> int | None:
    data = await state.get_data()
    return data.get("user_id")

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

@router.message(F.text == "Проверки")
async def open_checks_filters(message: Message, state: FSMContext):
    await show_filters_message(message, state)

@router.message(F.text == "Задачи")
async def open_tasks_filters(message: Message, state: FSMContext):
    await show_tasks_filters_message(message, state)

@router.callback_query(ChecksMenuCb.filter(F.action == "back"))
async def back_to_filters(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_filters_message(callback, state)

@router.callback_query(TasksMenuCb.filter(F.action == "back"))
async def back_to_tasks_filters(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_tasks_filters_message(callback, state)

@router.callback_query(
    ChecksMenuCb.filter(F.action.in_({"date_at", "finished_at", "deadline_at"}))
)
async def open_period_submenu(
    callback: CallbackQuery,
    callback_data: ChecksMenuCb,
    state: FSMContext,
):
    await open_range_calendar(callback, state, "checks", callback_data.action)

@router.callback_query(TasksMenuCb.filter(F.action == "deadline_period"))
async def open_tasks_deadline_period(
    callback: CallbackQuery,
    state: FSMContext,
):
    await open_range_calendar(callback, state, "tasks", "deadline_period")

@router.callback_query(TasksMenuCb.filter(F.action == "priority"))
async def open_task_priority(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Выберите приоритет:",
        reply_markup=task_priority_keyboard()
    )

@router.callback_query(TaskPriorityChoiceCb.filter())
async def process_task_priority_choice(
    callback: CallbackQuery,
    callback_data: TaskPriorityChoiceCb,
    state: FSMContext,
):
    value = callback_data.value
    if value == "clear":
        await remove_task_filter(state, "priority")
        await callback.answer("Фильтр приоритета сброшен")
        await show_tasks_filters_message(callback, state)
        return
    await save_task_filter(
        state,
        "priority",
        {
            "value": value,
            "label": TASK_PRIORITY_LABELS[value],
        }
    )
    await callback.answer("Приоритет сохранён")
    await show_tasks_filters_message(callback, state)

@router.callback_query(ChecksMenuCb.filter(F.action == "status"))
async def open_status_submenu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Выберите статус:",
        reply_markup=status_keyboard()
    )

@router.callback_query(StatusChoiceCb.filter())
async def process_status_choice(
    callback: CallbackQuery,
    callback_data: StatusChoiceCb,
    state: FSMContext,
):
    value = callback_data.value
    if value == "clear":
        await remove_filter(state, "status")
        await callback.answer("Статус сброшен")
        await show_filters_message(callback, state)
        return
    await save_filter(
        state,
        "status",
        {
            "value": value,
            "label": STATUS_LABELS[value],
        }
    )
    await callback.answer("Статус сохранён")
    await show_filters_message(callback, state)

@router.callback_query(ChecksMenuCb.filter(F.action == "overdue"))
async def open_overdue_submenu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Выберите значение фильтра «Просрочено»:",
        reply_markup=overdue_keyboard()
    )

@router.callback_query(OverdueChoiceCb.filter())
async def process_overdue_choice(
    callback: CallbackQuery,
    callback_data: OverdueChoiceCb,
    state: FSMContext,
):
    value = callback_data.value
    if value == "clear":
        await remove_filter(state, "overdue")
        await callback.answer("Фильтр сброшен")
        await show_filters_message(callback, state)
        return
    label = "Да" if value == "yes" else "Нет"
    await save_filter(
        state,
        "overdue",
        {
            "value": value == "yes",
            "label": label,
        }
    )
    await callback.answer("Значение сохранено")
    await show_filters_message(callback, state)

@router.callback_query(ChecksMenuCb.filter(F.action == "pattern"))
async def open_pattern_search(callback: CallbackQuery, state: FSMContext):
    user_id = await get_current_user_id(state)
    if user_id is None:
        await callback.answer("Не найден user_id. Войдите в систему заново.", show_alert=True)
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

@router.callback_query(ChecksMenuCb.filter(F.action == "clear_all"))
async def clear_all_filters(callback: CallbackQuery, state: FSMContext):
    await state.update_data(
        checks_filters={},
        calendar_context=None,
        available_patterns=[],
        pattern_prompt_message_id=None,
        pattern_results_message_id=None,
    )
    await callback.answer("Все фильтры сброшены")
    await show_filters_message(callback, state)

@router.callback_query(TasksMenuCb.filter(F.action == "clear_all"))
async def clear_all_task_filters_handler(callback: CallbackQuery, state: FSMContext):
    await clear_task_filters(state)
    await callback.answer("Все фильтры задач сброшены")
    await show_tasks_filters_message(callback, state)

@router.callback_query(ChecksMenuCb.filter(F.action == "apply"))
async def apply_filters(callback: CallbackQuery, state: FSMContext):
    filters = await get_filters(state)
    user_id = await get_current_user_id(state)
    try:
        response_data = await send_checks_filters_to_backend(
            user_id=user_id,
            filters=filters
        )
    except Exception as e:
        await callback.answer()
        await callback.message.answer(
            f"Не удалось отправить фильтры на бекэнд: {e}"
        )
        return
    print(response_data)
    await callback.answer(build_checks_status_legend())
    await callback.message.answer(format_checks_response(response_data))

@router.callback_query(TasksMenuCb.filter(F.action == "apply"))
async def apply_task_filters(callback: CallbackQuery, state: FSMContext):
    filters = await get_task_filters(state)
    user_id = await get_current_user_id(state)
    try:
        response_data = await send_tasks_filters_to_backend(
            user_id=user_id,
            filters=filters
        )
    except Exception as e:
        await callback.answer()
        await callback.message.answer(
            f"Не удалось отправить фильтры задач на бекэнд: {e}"
        )
        return
    print(response_data)
    await callback.answer()
    await callback.message.answer(format_tasks_response(response_data))