#Задачи
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, BufferedInputFile

from bot.constants import TASK_PRIORITY_LABELS, TASK_STATUS_LABELS
from bot.filters.tasks_common import (
    clear_task_filters,
    get_task_filters,
    remove_task_filter,
    save_task_filter,
)
from bot.formatters.summary import format_today_summary
from bot.formatters.tasks import format_tasks_response, get_tasks_items
from bot.handlers.bot_calendar import open_range_calendar
from bot.handlers.common import require_user_id, show_tasks_filters_message, toggle_mutually_exclusive_flag
from bot.keyboards.callbacks import TaskPriorityChoiceCb, TasksMenuCb
from bot.keyboards.tasks import task_priority_keyboard
from bot.services.connect_with_backend import send_tasks_filters_to_backend, fetch_tasks_today_summary
from bot.services.pdf_export import build_tasks_pdf_bytes

router = Router()

@router.message(F.text == "Задачи")
async def open_tasks_filters(message: Message, state: FSMContext):
    await show_tasks_filters_message(message, state)

@router.callback_query(TasksMenuCb.filter(F.action == "back"))
async def back_to_tasks_filters(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_tasks_filters_message(callback, state)

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

@router.callback_query(TasksMenuCb.filter(F.action == "toggle_show_my"))
async def toggle_show_my_tasks(callback: CallbackQuery, state: FSMContext):
    is_enabled = await toggle_mutually_exclusive_flag(
        state=state,
        get_filters_func=get_task_filters,
        save_filter_func=save_task_filter,
        remove_filter_func=remove_task_filter,
        current_key="show_my",
        opposite_key="made_by_me",
    )
    if is_enabled:
        await callback.answer("Фильтр «Показывать только мои задачи» включён")
    else:
        await callback.answer("Фильтр «Показывать только мои задачи» выключен")
    await show_tasks_filters_message(callback, state)

@router.callback_query(TasksMenuCb.filter(F.action == "toggle_made_by_me"))
async def toggle_made_by_me_tasks(callback: CallbackQuery, state: FSMContext):
    is_enabled = await toggle_mutually_exclusive_flag(
        state=state,
        get_filters_func=get_task_filters,
        save_filter_func=save_task_filter,
        remove_filter_func=remove_task_filter,
        current_key="made_by_me",
        opposite_key="show_my",
    )
    if is_enabled:
        await callback.answer("Фильтр «Показывать назначенные мной» включён")
    else:
        await callback.answer("Фильтр «Показывать назначенные мной» выключен")
    await show_tasks_filters_message(callback, state)

@router.callback_query(TasksMenuCb.filter(F.action == "today_summary"))
async def tasks_today_summary(callback: CallbackQuery, state: FSMContext):
    user_id = await require_user_id(callback, state)
    if user_id is None:
        return
    try:
        response_data = await fetch_tasks_today_summary(user_id)
    except Exception as e:
        await callback.answer()
        await callback.message.answer(
            f"Не удалось получить сводку по задачам: {e}"
        )
        return
    await callback.answer()
    await callback.message.answer(
        format_today_summary(response_data, "задач", TASK_STATUS_LABELS)
    )

@router.callback_query(TasksMenuCb.filter(F.action == "clear_all"))
async def clear_all_task_filters_handler(callback: CallbackQuery, state: FSMContext):
    await clear_task_filters(state)
    await callback.answer("Все фильтры задач сброшены")
    await show_tasks_filters_message(callback, state)


@router.callback_query(TasksMenuCb.filter(F.action == "apply"))
async def apply_task_filters(callback: CallbackQuery, state: FSMContext):
    filters = await get_task_filters(state)
    user_id = await require_user_id(callback, state)
    if user_id is None:
        return
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
    await callback.answer()
    items = get_tasks_items(response_data)
    if len(items) > 20:
        pdf_bytes = build_tasks_pdf_bytes(response_data)
        pdf_file = BufferedInputFile(pdf_bytes, filename="tasks_result.pdf")
        await callback.message.answer_document(
            document=pdf_file,
            caption="Найдено больше 20 задач, отправляю PDF."
        )
        return
    await callback.message.answer(format_tasks_response(response_data))