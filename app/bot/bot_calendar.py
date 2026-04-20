from datetime import date, datetime

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from menu import checks_filters_keyboard
from checks_calendar import FIELD_LABELS, build_filters_text, get_filters, save_filter

router = Router()

CALENDAR_CONTEXT_KEY = "calendar_context"


def normalize_to_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    raise ValueError(f"Неизвестный тип даты: {type(value)}")


async def open_range_calendar(
    target: Message | CallbackQuery,
    state: FSMContext,
    field: str,
):
    await state.update_data(**{
        CALENDAR_CONTEXT_KEY: {
            "field": field,
            "stage": "start",
            "start_date": None,
        }
    })

    text = f"Выберите дату начала для фильтра «{FIELD_LABELS[field]}»:"
    markup = await SimpleCalendar().start_calendar()

    if isinstance(target, CallbackQuery):
        await target.answer()
        await target.message.edit_text(text, reply_markup=markup)
    else:
        await target.answer(text, reply_markup=markup)


@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar_selection(
    callback_query: CallbackQuery,
    callback_data: dict,
    state: FSMContext,
):
    calendar = SimpleCalendar()
    selected, selected_date = await calendar.process_selection(callback_query, callback_data)

    if not selected:
        return

    selected_date = normalize_to_date(selected_date)

    data = await state.get_data()
    context = data.get(CALENDAR_CONTEXT_KEY)

    if not context:
        await callback_query.answer("Контекст календаря не найден", show_alert=True)
        return

    field = context["field"]
    stage = context["stage"]

    if stage == "start":
        await state.update_data(**{
            CALENDAR_CONTEXT_KEY: {
                "field": field,
                "stage": "end",
                "start_date": selected_date.isoformat(),
            }
        })

        await callback_query.answer()
        await callback_query.message.edit_text(
            f"Дата начала: {selected_date.strftime('%d.%m.%Y')}\n\n"
            f"Теперь выберите дату окончания для фильтра «{FIELD_LABELS[field]}»:",
            reply_markup=await SimpleCalendar().start_calendar(
                year=selected_date.year,
                month=selected_date.month
            )
        )
        return

    start_date = normalize_to_date(context["start_date"])
    end_date = selected_date

    if end_date < start_date:
        await callback_query.answer(
            "Дата окончания не может быть раньше даты начала",
            show_alert=True
        )
        await callback_query.message.edit_text(
            f"Дата начала: {start_date.strftime('%d.%m.%Y')}\n\n"
            f"Выберите корректную дату окончания для фильтра «{FIELD_LABELS[field]}»:",
            reply_markup=await SimpleCalendar().start_calendar(
                year=start_date.year,
                month=start_date.month
            )
        )
        return

    period_value = {
        "from": start_date.isoformat(),
        "to": end_date.isoformat(),
        "label": f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
    }

    await save_filter(state, field, period_value)
    await state.update_data(**{CALENDAR_CONTEXT_KEY: None})

    filters = await get_filters(state)
    text = build_filters_text(filters)
    markup = checks_filters_keyboard(filters)

    await callback_query.answer("Период сохранён")

    try:
        await callback_query.message.delete()
    except Exception:
        pass

    await callback_query.bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=text,
        reply_markup=markup
    )