#раздел задач
from aiogram.fsm.context import FSMContext

TASK_FILTERS_KEY = "tasks_filters"

TASK_FIELD_LABELS = {
    "deadline_period": "Сроки",
}

async def get_task_filters(state: FSMContext) -> dict:
    data = await state.get_data()
    return data.get(TASK_FILTERS_KEY, {})

async def save_task_filter(state: FSMContext, key: str, value: dict):
    filters = await get_task_filters(state)
    filters[key] = value
    await state.update_data(**{TASK_FILTERS_KEY: filters})

async def remove_task_filter(state: FSMContext, key: str):
    filters = await get_task_filters(state)
    filters.pop(key, None)
    await state.update_data(**{TASK_FILTERS_KEY: filters})

async def clear_task_filters(state: FSMContext):
    await state.update_data(**{TASK_FILTERS_KEY: {}})

def build_tasks_filters_text(filters: dict) -> str:
    show_my_label = "Да" if filters.get("show_my", {}).get("value") is True else "Нет"
    made_by_me_label = "Да" if filters.get("made_by_me", {}).get("value") is True else "Нет"
    lines = [
        "Выберите фильтры для раздела «Задачи».",
        "",
        f"• Сроки: {filters.get('deadline_period', {}).get('label', 'не выбрано')}",
        f"• Приоритет: {filters.get('priority', {}).get('label', 'не выбрано')}",
        f"• Показывать только мои задачи: {show_my_label}",
        f"• Показывать назначенные мной: {made_by_me_label}",
    ]
    return "\n".join(lines)