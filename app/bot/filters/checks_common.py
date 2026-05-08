from aiogram.fsm.context import FSMContext

FILTERS_KEY = "checks_filters"

FIELD_LABELS = {
    "date_at": "Приступить к выполнению",
    "finished_at": "Период даты завершения (фактического)",
    "deadline_at": "Период крайнего срока",
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
    show_my_label = "Да" if filters.get("show_my", {}).get("value") is True else "Нет"
    made_by_me_label = "Да" if filters.get("made_by_me", {}).get("value") is True else "Нет"
    lines = [
        "Выберите фильтры для раздела «Проверки».",
        "",
        f"• Приступить к выполнению: {filters.get('date_at', {}).get('label', 'не выбрано')}",
        f"• Период даты завершения (фактического): {filters.get('finished_at', {}).get('label', 'не выбрано')}",
        f"• Период крайнего срока: {filters.get('deadline_at', {}).get('label', 'не выбрано')}",
        f"• Статус: {filters.get('status', {}).get('label', 'не выбрано')}",
        f"• Просрочено: {filters.get('overdue', {}).get('label', 'не выбрано')}",
        f"• Шаблон чек-листа: {filters.get('pattern', {}).get('name', 'не выбрано')}",
        f"• Показывать только мои задачи: {show_my_label}",
        f"• Показывать назначенные мной: {made_by_me_label}",
    ]
    return "\n".join(lines)