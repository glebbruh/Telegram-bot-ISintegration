from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from menu import (
    ChecksMenuCb,
    OverdueChoiceCb,
    StatusChoiceCb,
    TemplateChoiceCb,
    checks_filters_keyboard,
    overdue_keyboard,
    status_keyboard,
    templates_results_keyboard,
)
from bot_calendar import open_range_calendar
from checks_calendar import build_filters_text, get_filters, remove_filter, save_filter

router = Router()

# Временный список шаблонов чек-листов.
# Потом можно заменить на данные с бекэнда.
CHECKLIST_TEMPLATES = [
    {"id": 1, "name": "пупи"},
    {"id": 2, "name": "вупи"},
    {"id": 3, "name": "пупи"},
    {"id": 4, "name": "пупи"},
    {"id": 5, "name": "пупи"},
    {"id": 6, "name": "пупи"},
    {"id": 7, "name": "пупи"},
    {"id": 8, "name": "пупи"},
    {"id": 9, "name": "пупи"},
    {"id": 10, "name": "пупи"},
    {"id": 11, "name": "пупи"}
]

STATUS_LABELS = {
    "new": "Новая",
    "in_progress": "В работе",
    "done": "Завершена",
    "cancelled": "Отменена",
}

async def show_filters_message(target: Message | CallbackQuery, state: FSMContext):
    filters = await get_filters(state)
    text = build_filters_text(filters)
    markup = checks_filters_keyboard(filters)

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=markup)
    else:
        await target.answer(text, reply_markup=markup)


@router.message(F.text == "Проверки")
async def open_checks_filters(message: Message, state: FSMContext):
    await show_filters_message(message, state)


@router.message(F.text == "Задачи")
async def open_tasks(message: Message):
    await message.answer("Раздел «Задачи» пока в разработке.")


@router.callback_query(ChecksMenuCb.filter(F.action == "back"))
async def back_to_filters(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_filters_message(callback, state)


@router.callback_query(
    ChecksMenuCb.filter(F.action.in_({"start_period", "finish_period", "deadline_period"}))
)
async def open_period_submenu(
    callback: CallbackQuery,
    callback_data: ChecksMenuCb,
    state: FSMContext,
):
    await open_range_calendar(callback, state, callback_data.action)

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


@router.callback_query(ChecksMenuCb.filter(F.action == "template"))
async def open_template_search(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "Введите часть названия шаблона чек-листа.\n"
        "Например: пожар, уборка, смена"
    )

@router.message()
async def process_template_search(message: Message, state: FSMContext):
    filters = await get_filters(state)
    query = (message.text or "").strip().lower()
    if query in {"проверки", "задачи", "/start"}:
        return
    results = [
        item for item in CHECKLIST_TEMPLATES
        if query in item["name"].lower()
    ][:10]
    if not results:
        return
    await message.answer(
        "Найдены шаблоны. Выберите один из списка:",
        reply_markup=templates_results_keyboard(results)
    )


@router.callback_query(TemplateChoiceCb.filter())
async def process_template_choice(
    callback: CallbackQuery,
    callback_data: TemplateChoiceCb,
    state: FSMContext,
):
    template_id = callback_data.template_id
    template = next(
        (item for item in CHECKLIST_TEMPLATES if item["id"] == template_id),
        None
    )

    if not template:
        await callback.answer("Шаблон не найден", show_alert=True)
        return

    await save_filter(
        state,
        "template",
        {
            "id": template["id"],
            "name": template["name"],
        }
    )
    await callback.answer("Шаблон сохранён")
    await show_filters_message(callback, state)


@router.callback_query(ChecksMenuCb.filter(F.action == "apply"))
async def apply_filters(callback: CallbackQuery, state: FSMContext):
    filters = await get_filters(state)
    payload = {
        "section": "checks",
        "filters": filters,
    }
    # Потом сюда можно будет добавить отправку payload на бекэнд.
    # Сейчас только заглушка.
    print(payload)
    await callback.answer()
    await callback.message.answer("Спасибо, что оставили сообщение!")