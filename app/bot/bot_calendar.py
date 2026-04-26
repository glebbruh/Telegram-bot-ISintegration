from datetime import date, datetime

from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from menu import checks_filters_keyboard, tasks_filters_keyboard
from checks_common import (
    FIELD_LABELS as CHECKS_FIELD_LABELS,
    build_filters_text as build_checks_filters_text,
    get_filters as get_checks_filters,
    remove_filter as remove_checks_filter,
    save_filter as save_checks_filter,
)
from tasks_common import (
    TASK_FIELD_LABELS,
    build_tasks_filters_text,
    get_task_filters,
    remove_task_filter,
    save_task_filter,
)

router = Router()

CALENDAR_CONTEXT_KEY = "calendar_context"

class CalendarExtraCb(CallbackData, prefix="calendar_extra"):
    action: str  # back / clear / today

class CustomSimpleCalendar(SimpleCalendar):
    def __init__(self):
        super().__init__(
            cancel_btn="Назад",
            today_btn="Сегодня",
        )
        self._labels.months = [
            "Янв", "Фев", "Мар", "Апр", "Май", "Июн",
            "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек",
        ]
        self._labels.days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    async def start_calendar(self, year: int | None = None, month: int | None = None):
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        markup = await super().start_calendar(year=year, month=month)
        return replace_calendar_footer(markup)

def normalize_to_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    raise ValueError(f"Неизвестный тип даты: {type(value)}")

def create_calendar() -> CustomSimpleCalendar:
    return CustomSimpleCalendar()

def replace_calendar_footer(markup):
    keyboard = markup.inline_keyboard[:-1]
    custom_footer = [
        InlineKeyboardButton(
            text="Назад",
            callback_data=CalendarExtraCb(action="back").pack(),
        ),
        InlineKeyboardButton(
            text="Сбросить",
            callback_data=CalendarExtraCb(action="clear").pack(),
        ),
        InlineKeyboardButton(
            text="Сегодня",
            callback_data=CalendarExtraCb(action="today").pack(),
        ),
    ]
    keyboard.append(custom_footer)
    markup.inline_keyboard = keyboard
    return markup

async def build_calendar_markup(year: int | None = None, month: int | None = None):
    cal = create_calendar()
    if year is not None and month is not None:
        markup = await cal.start_calendar(year=year, month=month)
    else:
        markup = await cal.start_calendar()
    return markup

def get_calendar_config(section: str):
    if section == "checks":
        return {
            "field_labels": CHECKS_FIELD_LABELS,
            "get_filters": get_checks_filters,
            "save_filter": save_checks_filter,
            "remove_filter": remove_checks_filter,
            "build_text": build_checks_filters_text,
            "build_keyboard": checks_filters_keyboard,
        }
    if section == "tasks":
        return {
            "field_labels": TASK_FIELD_LABELS,
            "get_filters": get_task_filters,
            "save_filter": save_task_filter,
            "remove_filter": remove_task_filter,
            "build_text": build_tasks_filters_text,
            "build_keyboard": tasks_filters_keyboard,
        }
    raise ValueError(f"Неизвестный раздел: {section}")

async def send_filters_panel(callback_query: CallbackQuery, state: FSMContext, section: str):
    config = get_calendar_config(section)
    filters = await config["get_filters"](state)
    text = config["build_text"](filters)
    markup = config["build_keyboard"](filters)
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    await callback_query.bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=text,
        reply_markup=markup,
    )

async def open_range_calendar(
    target: Message | CallbackQuery,
    state: FSMContext,
    section: str,
    field: str,
):
    config = get_calendar_config(section)
    field_labels = config["field_labels"]
    await state.update_data(**{
        CALENDAR_CONTEXT_KEY: {
            "section": section,
            "field": field,
            "stage": "start",
            "start_date": None,
        }
    })
    text = f"Выберите дату начала для фильтра «{field_labels[field]}»:"
    markup = await build_calendar_markup()
    if isinstance(target, CallbackQuery):
        await target.answer()
        await target.message.edit_text(text, reply_markup=markup)
    else:
        await target.answer(text, reply_markup=markup)

@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar_selection(
    callback_query: CallbackQuery,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
):
    calendar = create_calendar()
    selected, selected_date = await calendar.process_selection(callback_query, callback_data)
    if not selected:
        return
    selected_date = normalize_to_date(selected_date)
    data = await state.get_data()
    context = data.get(CALENDAR_CONTEXT_KEY)
    if not context:
        await callback_query.answer("Контекст календаря не найден", show_alert=True)
        return
    section = context["section"]
    field = context["field"]
    stage = context["stage"]
    config = get_calendar_config(section)
    field_labels = config["field_labels"]
    save_filter_func = config["save_filter"]
    if stage == "start":
        await state.update_data(**{
            CALENDAR_CONTEXT_KEY: {
                "section": section,
                "field": field,
                "stage": "end",
                "start_date": selected_date.isoformat(),
            }
        })
        await callback_query.answer()
        await callback_query.message.edit_text(
            f"Дата начала: {selected_date.strftime('%d.%m.%Y')}\n\n"
            f"Теперь выберите дату окончания для фильтра «{field_labels[field]}»:",
            reply_markup=await build_calendar_markup(
                year=selected_date.year,
                month=selected_date.month,
            ),
        )
        return
    start_date = normalize_to_date(context["start_date"])
    end_date = selected_date
    if end_date < start_date:
        await callback_query.answer(
            "Дата окончания не может быть раньше даты начала",
            show_alert=True,
        )
        await callback_query.message.edit_text(
            f"Дата начала: {start_date.strftime('%d.%m.%Y')}\n\n"
            f"Выберите корректную дату окончания для фильтра «{field_labels[field]}»:",
            reply_markup=await build_calendar_markup(
                year=start_date.year,
                month=start_date.month,
            ),
        )
        return
    period_value = {
        "from": start_date.isoformat(),
        "to": end_date.isoformat(),
        "label": f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
    }
    await save_filter_func(state, field, period_value)
    await state.update_data(**{CALENDAR_CONTEXT_KEY: None})
    await callback_query.answer("Период сохранён")
    await send_filters_panel(callback_query, state, section)


@router.callback_query(CalendarExtraCb.filter(F.action == "back"))
async def calendar_back(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    context = data.get(CALENDAR_CONTEXT_KEY)
    section = context["section"] if context else "checks"
    await state.update_data(**{CALENDAR_CONTEXT_KEY: None})
    await callback.answer()
    await send_filters_panel(callback, state, section)


@router.callback_query(CalendarExtraCb.filter(F.action == "clear"))
async def calendar_clear(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    context = data.get(CALENDAR_CONTEXT_KEY)
    section = context["section"] if context else "checks"
    if context and context.get("field"):
        config = get_calendar_config(section)
        await config["remove_filter"](state, context["field"])
    await state.update_data(**{CALENDAR_CONTEXT_KEY: None})
    await callback.answer("Фильтр по дате сброшен")
    await send_filters_panel(callback, state, section)


@router.callback_query(CalendarExtraCb.filter(F.action == "today"))
async def calendar_today(callback: CallbackQuery, state: FSMContext):
    today = date.today()
    data = await state.get_data()
    context = data.get(CALENDAR_CONTEXT_KEY)
    if not context:
        await callback.answer("Контекст календаря не найден", show_alert=True)
        return
    section = context["section"]
    field = context["field"]
    stage = context["stage"]
    config = get_calendar_config(section)
    field_labels = config["field_labels"]
    if stage == "start":
        await state.update_data(**{
            CALENDAR_CONTEXT_KEY: {
                "section": section,
                "field": field,
                "stage": "end",
                "start_date": today.isoformat(),
            }
        })
        await callback.answer("Дата начала = сегодня")
        await callback.message.edit_text(
            f"Дата начала: {today.strftime('%d.%m.%Y')}\n\n"
            f"Теперь выберите дату окончания для фильтра «{field_labels[field]}»:",
            reply_markup=await build_calendar_markup(
                year=today.year,
                month=today.month,
            ),
        )
        return
    start_date = normalize_to_date(context["start_date"])
    end_date = today
    if end_date < start_date:
        await callback.answer(
            "Сегодня раньше даты начала",
            show_alert=True,
        )
        return
    period_value = {
        "from": start_date.isoformat(),
        "to": end_date.isoformat(),
        "label": f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
    }
    await config["save_filter"](state, field, period_value)
    await state.update_data(**{CALENDAR_CONTEXT_KEY: None})
    await callback.answer("Период сохранён")
    await send_filters_panel(callback, state, section)