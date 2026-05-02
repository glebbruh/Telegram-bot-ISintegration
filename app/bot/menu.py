#меню бота
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

class ChecksMenuCb(CallbackData, prefix="checks_menu"):
    action: str

class StatusChoiceCb(CallbackData, prefix="status"):
    value: str

class OverdueChoiceCb(CallbackData, prefix="overdue"):
    value: str

class TemplateChoiceCb(CallbackData, prefix="template"):
    template_id: int

class TasksMenuCb(CallbackData, prefix="tasks_menu"):
    action: str

class TaskPriorityChoiceCb(CallbackData, prefix="task_priority"):
    value: str

def main_sections_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Проверки"), KeyboardButton(text="Задачи")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел"
    )


def checks_filters_keyboard(filters: dict | None = None) -> InlineKeyboardMarkup:
    filters = filters or {}
    start_text = "Приступить"
    if filters.get("start_period"):
        start_text += f" ✅ {filters['start_period']['label']}"
    finish_text = "Период даты завершения"
    if filters.get("finish_period"):
        finish_text += f" ✅ {filters['finish_period']['label']}"
    deadline_text = "Период крайнего срока"
    if filters.get("deadline_period"):
        deadline_text += f" ✅ {filters['deadline_period']['label']}"
    status_text = "Статус"
    if filters.get("status"):
        status_text += f" ✅ {filters['status']['label']}"
    overdue_text = "Просрочено"
    if filters.get("overdue"):
        overdue_text += f" ✅ {filters['overdue']['label']}"
    template_text = "Шаблоны чек-листов"
    if filters.get("template"):
        template_text += f" ✅ {filters['template']['name']}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=start_text,
                    callback_data=ChecksMenuCb(action="start_period").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=finish_text,
                    callback_data=ChecksMenuCb(action="finish_period").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=deadline_text,
                    callback_data=ChecksMenuCb(action="deadline_period").pack()
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
                    text=template_text,
                    callback_data=ChecksMenuCb(action="template").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Сбросить все фильтр",
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
                    text="Новая",
                    callback_data=StatusChoiceCb(value="new").pack()
                ),
                InlineKeyboardButton(
                    text="В работе",
                    callback_data=StatusChoiceCb(value="in_progress").pack()
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Завершена",
                    callback_data=StatusChoiceCb(value="done").pack()
                ),
                InlineKeyboardButton(
                    text="Отменена",
                    callback_data=StatusChoiceCb(value="cancelled").pack()
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

def templates_results_keyboard(results: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in results:
        builder.button(
            text=item["name"],
            callback_data=TemplateChoiceCb(template_id=item["id"]).pack()
        )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=ChecksMenuCb(action="back").pack()
        )
    )
    return builder.as_markup()

def tasks_filters_keyboard(filters: dict | None = None) -> InlineKeyboardMarkup:
    filters = filters or {}
    deadline_text = "Сроки"
    if filters.get("deadline_period"):
        deadline_text += f" ✅ {filters['deadline_period']['label']}"
    priority_text = "Приоритет"
    if filters.get("priority"):
        priority_text += f" ✅ {filters['priority']['label']}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=deadline_text,
                    callback_data=TasksMenuCb(action="deadline_period").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=priority_text,
                    callback_data=TasksMenuCb(action="priority").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Сбросить все фильтры",
                    callback_data=TasksMenuCb(action="clear_all").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Получить данные",
                    callback_data=TasksMenuCb(action="apply").pack()
                )
            ],
        ]
    )

def task_priority_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Без приоритета",
                    callback_data=TaskPriorityChoiceCb(value="none").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Низкий",
                    callback_data=TaskPriorityChoiceCb(value="low").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Средний",
                    callback_data=TaskPriorityChoiceCb(value="medium").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Высокий",
                    callback_data=TaskPriorityChoiceCb(value="high").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=TasksMenuCb(action="back").pack()
                ),
                InlineKeyboardButton(
                    text="Сбросить фильтр",
                    callback_data=TaskPriorityChoiceCb(value="clear").pack()
                )
            ]
        ]
    )