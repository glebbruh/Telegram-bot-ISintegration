#Проверки
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, BufferedInputFile

from bot.constants import CHECK_STATUS_LABELS, CHECK_STATUS_LABELS_LOWER
from bot.filters.checks_common import get_filters, remove_filter, save_filter
from bot.formatters.checks import build_checks_status_legend, format_checks_response, get_checks_items
from bot.formatters.summary import format_today_summary
from bot.handlers.bot_calendar import open_range_calendar
from bot.handlers.common import get_current_user_id, show_filters_message, toggle_mutually_exclusive_flag
from bot.keyboards.callbacks import ChecksMenuCb, OverdueChoiceCb, StatusChoiceCb
from bot.keyboards.checks import overdue_keyboard, status_keyboard
from bot.services.connect_with_backend import send_checks_filters_to_backend, fetch_checks_today_summary
from bot.services.pdf_export import build_checks_pdf_bytes

router = Router()

@router.message(F.text == "Проверки")
async def open_checks_filters(message: Message, state: FSMContext):
    await show_filters_message(message, state)

@router.callback_query(ChecksMenuCb.filter(F.action == "back"))
async def back_to_filters(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_filters_message(callback, state)

@router.callback_query(
    ChecksMenuCb.filter(F.action.in_({"date_at", "finished_at", "deadline_at"}))
)
async def open_period_submenu(
    callback: CallbackQuery,
    callback_data: ChecksMenuCb,
    state: FSMContext,
):
    await open_range_calendar(callback, state, "checks", callback_data.action)

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
            "label": CHECK_STATUS_LABELS[value],
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

@router.callback_query(ChecksMenuCb.filter(F.action == "toggle_show_my"))
async def toggle_show_my_checks(callback: CallbackQuery, state: FSMContext):
    is_enabled = await toggle_mutually_exclusive_flag(
        state=state,
        get_filters_func=get_filters,
        save_filter_func=save_filter,
        remove_filter_func=remove_filter,
        current_key="show_my",
        opposite_key="made_by_me",
    )
    if is_enabled:
        await callback.answer("Фильтр «Показывать только мои задачи» включён")
    else:
        await callback.answer("Фильтр «Показывать только мои задачи» выключен")
    await show_filters_message(callback, state)

@router.callback_query(ChecksMenuCb.filter(F.action == "toggle_made_by_me"))
async def toggle_made_by_me_checks(callback: CallbackQuery, state: FSMContext):
    is_enabled = await toggle_mutually_exclusive_flag(
        state=state,
        get_filters_func=get_filters,
        save_filter_func=save_filter,
        remove_filter_func=remove_filter,
        current_key="made_by_me",
        opposite_key="show_my",
    )
    if is_enabled:
        await callback.answer("Фильтр «Показывать назначенные мной» включён")
    else:
        await callback.answer("Фильтр «Показывать назначенные мной» выключен")
    await show_filters_message(callback, state)

@router.callback_query(ChecksMenuCb.filter(F.action == "today_summary"))
async def checks_today_summary(callback: CallbackQuery, state: FSMContext):
    user_id = await get_current_user_id(state)
    try:
        response_data = await fetch_checks_today_summary(user_id)
    except Exception as e:
        await callback.answer()
        await callback.message.answer(
            f"Не удалось получить сводку по проверкам: {e}"
        )
        return
    await callback.answer()
    await callback.message.answer(
        format_today_summary(response_data, "проверок", CHECK_STATUS_LABELS_LOWER)
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
    await callback.answer()
    items = get_checks_items(response_data)
    await callback.message.answer(build_checks_status_legend())
    if len(items) > 20:
        pdf_bytes = build_checks_pdf_bytes(response_data)
        pdf_file = BufferedInputFile(pdf_bytes, filename="checks_result.pdf")
        await callback.message.answer_document(
            document=pdf_file,
            caption="Найдено больше 20 проверок, отправляю PDF."
        )
        return
    await callback.message.answer(format_checks_response(response_data))