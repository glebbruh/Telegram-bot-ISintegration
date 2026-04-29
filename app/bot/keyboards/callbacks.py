from aiogram.filters.callback_data import CallbackData

class ChecksMenuCb(CallbackData, prefix="checks_menu"):
    action: str

class StatusChoiceCb(CallbackData, prefix="status"):
    value: str

class OverdueChoiceCb(CallbackData, prefix="overdue"):
    value: str

class PatternChoiceCb(CallbackData, prefix="pattern"):
    pattern_id: int

class TasksMenuCb(CallbackData, prefix="tasks_menu"):
    action: str

class TaskPriorityChoiceCb(CallbackData, prefix="task_priority"):
    value: str

class LogoutConfirmCb(CallbackData, prefix="logout"):
    action: str