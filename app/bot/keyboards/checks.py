from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.callbacks import (
    ChecksMenuCb,
    OverdueChoiceCb,
    PatternChoiceCb,
    StatusChoiceCb,
)

def checks_filters_keyboard(filters: dict | None = None) -> InlineKeyboardMarkup:
    filters = filters or {}
    start_text = "Приступить к выполнению"
    if filters.get("date_at"):
        start_text += f" ✅ {filters['date_at']['label']}"
    finish_text = "Период даты завершения"
    if filters.get("finished_at"):
        finish_text += f" ✅ {filters['finished_at']['label']}"
    deadline_text = "Период крайнего срока"
    if filters.get("deadline_at"):
        deadline_text += f" ✅ {filters['deadline_at']['label']}"
    status_text = "Статус"
    if filters.get("status"):
        status_text += f" ✅ {filters['status']['label']}"
    overdue_text = "Просрочено"
    if filters.get("overdue"):
        overdue_text += f" ✅ {filters['overdue']['label']}"
    pattern_text = "Шаблоны чек-листов"
    if filters.get("pattern"):
        pattern_text += f" ✅ {filters['pattern']['name']}"
    show_my_text = "Показывать только мои задачи"
    if filters.get("show_my", {}).get("value") is True:
        show_my_text += "✅"
    made_by_me_text = "Показывать назначенные мной"
    if filters.get("made_by_me", {}).get("value") is True:
        made_by_me_text += "✅"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=start_text,
                    callback_data=ChecksMenuCb(action="date_at").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=finish_text,
                    callback_data=ChecksMenuCb(action="finished_at").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=deadline_text,
                    callback_data=ChecksMenuCb(action="deadline_at").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=status_text,
                    callback_data=ChecksMenuCb(action="status").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=overdue_text,
                    callback_data=ChecksMenuCb(action="overdue").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=pattern_text,
                    callback_data=ChecksMenuCb(action="pattern").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=show_my_text,
                    callback_data=ChecksMenuCb(action="toggle_show_my").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=made_by_me_text,
                    callback_data=ChecksMenuCb(action="toggle_made_by_me").pack()
                )
            ],
            [
              InlineKeyboardButton(
                  text="Сводка на сегодня",
                  callback_data=ChecksMenuCb(action="today_summary").pack()
              )
            ],
            [
                InlineKeyboardButton(
                    text="Сбросить все фильтры",
                    callback_data=ChecksMenuCb(action="clear_all").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Получить данные",
                    callback_data=ChecksMenuCb(action="apply").pack()
                )
            ],
        ]
    )

def status_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Назначено",
                    callback_data=StatusChoiceCb(value="created").pack()
                ),
                InlineKeyboardButton(
                    text="В работе",
                    callback_data=StatusChoiceCb(value="process").pack()
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Завершено",
                    callback_data=StatusChoiceCb(value="completed").pack()
                ),
                InlineKeyboardButton(
                    text="Валидация",
                    callback_data=StatusChoiceCb(value="verification").pack()
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Сбросить",
                    callback_data=StatusChoiceCb(value="clear").pack()
                ),
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=ChecksMenuCb(action="back").pack()
                ),
            ]
        ]
    )


def overdue_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да",
                    callback_data=OverdueChoiceCb(value="yes").pack()
                ),
                InlineKeyboardButton(
                    text="Нет",
                    callback_data=OverdueChoiceCb(value="no").pack()
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Сбросить",
                    callback_data=OverdueChoiceCb(value="clear").pack()
                ),
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=ChecksMenuCb(action="back").pack()
                ),
            ]
        ]
    )

def patterns_results_keyboard(results: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in results:
        builder.button(
            text=item["name"],
            callback_data=PatternChoiceCb(pattern_id=item["id"]).pack()
        )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=ChecksMenuCb(action="back").pack()
        )
    )
    return builder.as_markup()