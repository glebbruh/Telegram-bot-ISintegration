from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.callbacks import TaskPriorityChoiceCb, TasksMenuCb

def tasks_filters_keyboard(filters: dict | None = None) -> InlineKeyboardMarkup:
    filters = filters or {}
    deadline_text = "Сроки"
    if filters.get("deadline_period"):
        deadline_text += f" ✅ {filters['deadline_period']['label']}"
    priority_text = "Приоритет"
    if filters.get("priority"):
        priority_text += f" ✅ {filters['priority']['label']}"
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
                    text=show_my_text,
                    callback_data=TasksMenuCb(action="toggle_show_my").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=made_by_me_text,
                    callback_data=TasksMenuCb(action="toggle_made_by_me").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Сводка на сегодня",
                    callback_data=TasksMenuCb(action="today_summary").pack()
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
                    text="Сбросить фильтры",
                    callback_data=TaskPriorityChoiceCb(value="clear").pack()
                )
            ]
        ]
    )