from aiogram.fsm.context import FSMContext

FILTERS_KEY = "checks_filters"

FIELD_LABELS = {
    "start_period": "Приступить",
    "finish_period": "Период даты завершения",
    "deadline_period": "Период крайнего срока",
}

async def get_filters(state: FSMContext) -> dict:
    data = await state.get_data()
    return data.get(FILTERS_KEY, {})

async def save_filter(state: FSMContext, key: str, value: dict):
    filters = await get_filters(state)
    filters[key] = value
    await state.update_data(**{FILTERS_KEY: filters})

async def remove_filter(state: FSMContext, key: str):
    filters = await get_filters(state)
    filters.pop(key, None)
    await state.update_data(**{FILTERS_KEY: filters})

def build_filters_text(filters: dict) -> str:
    lines = [
        "Выберите фильтры для раздела «Проверки».",
        "",
        f"• Приступить: {filters.get('start_period', {}).get('label', 'не выбрано')}",
        f"• Период даты завершения: {filters.get('finish_period', {}).get('label', 'не выбрано')}",
        f"• Период крайнего срока: {filters.get('deadline_period', {}).get('label', 'не выбрано')}",
        f"• Статус: {filters.get('status', {}).get('label', 'не выбрано')}",
        f"• Просрочено: {filters.get('overdue', {}).get('label', 'не выбрано')}",
        f"• Шаблон чек-листа: {filters.get('template', {}).get('name', 'не выбрано')}",
    ]
    return "\n".join(lines)