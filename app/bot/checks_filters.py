# import re
# from datetime import date, datetime, timedelta
#
# from aiogram import F, Router
# from aiogram.filters import StateFilter
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.types import CallbackQuery, Message
#
# from menu import (
#     ChecksMenuCb,
#     OverdueChoiceCb,
#     PeriodChoiceCb,
#     StatusChoiceCb,
#     TemplateChoiceCb,
#     checks_filters_keyboard,
#     overdue_keyboard,
#     period_keyboard,
#     status_keyboard,
#     templates_results_keyboard,
# )
#
# router = Router()
#
# # Временный список шаблонов чек-листов.
# # Потом можно заменить на данные с бекэнда.
# CHECKLIST_TEMPLATES = [
#     {"id": 1, "name": "пупи"},
#     {"id": 2, "name": "вупи"},
#     {"id": 3, "name": "пупи"},
#     {"id": 4, "name": "пупи"},
#     {"id": 5, "name": "пупи"},
#     {"id": 6, "name": "пупи"},
#     {"id": 7, "name": "пупи"},
#     {"id": 8, "name": "пупи"},
#     {"id": 9, "name": "пупи"},
#     {"id": 10, "name": "пупи"},
#     {"id": 11, "name": "пупи"}
# ]
#
# STATUS_LABELS = {
#     "new": "Новая",
#     "in_progress": "В работе",
#     "done": "Завершена",
#     "cancelled": "Отменена",
# }
#
# FIELD_LABELS = {
#     "start_period": "Приступить",
#     "finish_period": "Период даты завершения",
#     "deadline_period": "Период крайнего срока",
# }
#
# FILTERS_KEY = "checks_filters"
# CURRENT_PERIOD_FIELD_KEY = "current_period_field"
#
#
# class ChecksFilterStates(StatesGroup):
#     waiting_custom_period = State()
#     waiting_template_search = State()
#
#
# async def get_filters(state: FSMContext) -> dict:
#     data = await state.get_data()
#     return data.get(FILTERS_KEY, {})
#
#
# async def save_filter(state: FSMContext, key: str, value: dict):
#     filters = await get_filters(state)
#     filters[key] = value
#     await state.update_data(**{FILTERS_KEY: filters})
#
#
# async def remove_filter(state: FSMContext, key: str):
#     filters = await get_filters(state)
#     filters.pop(key, None)
#     await state.update_data(**{FILTERS_KEY: filters})
#
#
# def build_filters_text(filters: dict) -> str:
#     lines = [
#         "Выберите фильтры для раздела «Проверки».",
#         "",
#         f"• Приступить: {filters.get('start_period', {}).get('label', 'не выбрано')}",
#         f"• Период даты завершения: {filters.get('finish_period', {}).get('label', 'не выбрано')}",
#         f"• Период крайнего срока: {filters.get('deadline_period', {}).get('label', 'не выбрано')}",
#         f"• Статус: {filters.get('status', {}).get('label', 'не выбрано')}",
#         f"• Просрочено: {filters.get('overdue', {}).get('label', 'не выбрано')}",
#         f"• Шаблон чек-листа: {filters.get('template', {}).get('name', 'не выбрано')}",
#     ]
#     return "\n".join(lines)
#
#
# def make_quick_period(value: str) -> dict:
#     today = date.today()
#
#     if value == "today":
#         date_from = today
#         date_to = today
#         label = "Сегодня"
#     elif value == "7d":
#         date_from = today
#         date_to = today + timedelta(days=7)
#         label = "7 дней"
#     elif value == "30d":
#         date_from = today
#         date_to = today + timedelta(days=30)
#         label = "30 дней"
#     else:
#         raise ValueError("Неизвестный быстрый период")
#
#     return {
#         "from": date_from.isoformat(),
#         "to": date_to.isoformat(),
#         "label": label,
#     }
#
#
# def parse_custom_period(text: str) -> dict | None:
#     """
#     Ожидаемый формат:
#     01.05.2026 - 15.05.2026
#     """
#     pattern = r"^\s*(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})\s*$"
#     match = re.match(pattern, text)
#     if not match:
#         return None
#
#     start_str, end_str = match.groups()
#
#     try:
#         start_date = datetime.strptime(start_str, "%d.%m.%Y").date()
#         end_date = datetime.strptime(end_str, "%d.%m.%Y").date()
#     except ValueError:
#         return None
#
#     if start_date > end_date:
#         return None
#
#     return {
#         "from": start_date.isoformat(),
#         "to": end_date.isoformat(),
#         "label": f"{start_str} - {end_str}",
#     }
#
#
# async def show_filters_message(target: Message | CallbackQuery, state: FSMContext):
#     filters = await get_filters(state)
#     text = build_filters_text(filters)
#     markup = checks_filters_keyboard(filters)
#
#     if isinstance(target, CallbackQuery):
#         await target.message.edit_text(text, reply_markup=markup)
#     else:
#         await target.answer(text, reply_markup=markup)
#
#
# @router.message(F.text == "Проверки")
# async def open_checks_filters(message: Message, state: FSMContext):
#     await show_filters_message(message, state)
#
#
# @router.message(F.text == "Задачи")
# async def open_tasks(message: Message):
#     await message.answer("Раздел «Задачи» пока в разработке.")
#
#
# @router.callback_query(ChecksMenuCb.filter(F.action == "back"))
# async def back_to_filters(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     await show_filters_message(callback, state)
#
#
# @router.callback_query(
#     ChecksMenuCb.filter(F.action.in_({"start_period", "finish_period", "deadline_period"}))
# )
# async def open_period_submenu(
#     callback: CallbackQuery,
#     callback_data: ChecksMenuCb,
# ):
#     field = callback_data.action
#     field_label = FIELD_LABELS[field]
#
#     await callback.answer()
#     await callback.message.edit_text(
#         f"Выберите период для фильтра «{field_label}»:",
#         reply_markup=period_keyboard(field)
#     )
#
#
# @router.callback_query(PeriodChoiceCb.filter())
# async def process_period_choice(
#     callback: CallbackQuery,
#     callback_data: PeriodChoiceCb,
#     state: FSMContext,
# ):
#     field = callback_data.field
#     value = callback_data.value
#
#     if value in {"today", "7d", "30d"}:
#         period_data = make_quick_period(value)
#         await save_filter(state, field, period_data)
#         await callback.answer("Период сохранён")
#         await show_filters_message(callback, state)
#         return
#
#     if value == "clear":
#         await remove_filter(state, field)
#         await callback.answer("Фильтр сброшен")
#         await show_filters_message(callback, state)
#         return
#
#     if value == "custom":
#         await state.update_data(**{CURRENT_PERIOD_FIELD_KEY: field})
#         await state.set_state(ChecksFilterStates.waiting_custom_period)
#         await callback.answer()
#         await callback.message.answer(
#             f"Введите период для фильтра «{FIELD_LABELS[field]}» "
#             f"в формате:\nДД.ММ.ГГГГ - ДД.ММ.ГГГГ\n\n"
#             f"Например:\n01.05.2026 - 15.05.2026"
#         )
#         return
#
#
# @router.message(StateFilter(ChecksFilterStates.waiting_custom_period))
# async def process_custom_period_input(message: Message, state: FSMContext):
#     text = (message.text or "").strip()
#     parsed = parse_custom_period(text)
#
#     if not parsed:
#         await message.answer(
#             "Некорректный формат периода.\n"
#             "Введите так:\nДД.ММ.ГГГГ - ДД.ММ.ГГГГ"
#         )
#         return
#
#     data = await state.get_data()
#     field = data.get(CURRENT_PERIOD_FIELD_KEY)
#
#     if not field:
#         await message.answer("Не удалось определить, для какого фильтра сохранять период.")
#         await state.set_state(None)
#         return
#
#     await save_filter(state, field, parsed)
#     await state.update_data(**{CURRENT_PERIOD_FIELD_KEY: None})
#     await state.set_state(None)
#
#     await message.answer("Период сохранён.")
#     await show_filters_message(message, state)
#
#
# @router.callback_query(ChecksMenuCb.filter(F.action == "status"))
# async def open_status_submenu(callback: CallbackQuery):
#     await callback.answer()
#     await callback.message.edit_text(
#         "Выберите статус:",
#         reply_markup=status_keyboard()
#     )
#
#
# @router.callback_query(StatusChoiceCb.filter())
# async def process_status_choice(
#     callback: CallbackQuery,
#     callback_data: StatusChoiceCb,
#     state: FSMContext,
# ):
#     value = callback_data.value
#
#     if value == "clear":
#         await remove_filter(state, "status")
#         await callback.answer("Статус сброшен")
#         await show_filters_message(callback, state)
#         return
#
#     await save_filter(
#         state,
#         "status",
#         {
#             "value": value,
#             "label": STATUS_LABELS[value],
#         }
#     )
#     await callback.answer("Статус сохранён")
#     await show_filters_message(callback, state)
#
#
# @router.callback_query(ChecksMenuCb.filter(F.action == "overdue"))
# async def open_overdue_submenu(callback: CallbackQuery):
#     await callback.answer()
#     await callback.message.edit_text(
#         "Выберите значение фильтра «Просрочено»:",
#         reply_markup=overdue_keyboard()
#     )
#
#
# @router.callback_query(OverdueChoiceCb.filter())
# async def process_overdue_choice(
#     callback: CallbackQuery,
#     callback_data: OverdueChoiceCb,
#     state: FSMContext,
# ):
#     value = callback_data.value
#
#     if value == "clear":
#         await remove_filter(state, "overdue")
#         await callback.answer("Фильтр сброшен")
#         await show_filters_message(callback, state)
#         return
#
#     label = "Да" if value == "yes" else "Нет"
#
#     await save_filter(
#         state,
#         "overdue",
#         {
#             "value": value == "yes",
#             "label": label,
#         }
#     )
#     await callback.answer("Значение сохранено")
#     await show_filters_message(callback, state)
#
#
# @router.callback_query(ChecksMenuCb.filter(F.action == "template"))
# async def open_template_search(callback: CallbackQuery, state: FSMContext):
#     await state.set_state(ChecksFilterStates.waiting_template_search)
#     await callback.answer()
#     await callback.message.answer(
#         "Введите часть названия шаблона чек-листа.\n"
#         "Например: пожар, уборка, смена"
#     )
#
#
# @router.message(StateFilter(ChecksFilterStates.waiting_template_search))
# async def process_template_search(message: Message, state: FSMContext):
#     query = (message.text or "").strip().lower()
#
#     if not query:
#         await message.answer("Введите хотя бы один символ для поиска.")
#         return
#
#     results = [
#         item for item in CHECKLIST_TEMPLATES
#         if query in item["name"].lower()
#     ][:10]
#
#     if not results:
#         await message.answer("Ничего не найдено. Введите другой запрос.")
#         return
#
#     await state.set_state(None)
#     await message.answer(
#         "Найдены шаблоны. Выберите один из списка:",
#         reply_markup=templates_results_keyboard(results)
#     )
#
#
# @router.callback_query(TemplateChoiceCb.filter())
# async def process_template_choice(
#     callback: CallbackQuery,
#     callback_data: TemplateChoiceCb,
#     state: FSMContext,
# ):
#     template_id = callback_data.template_id
#     template = next(
#         (item for item in CHECKLIST_TEMPLATES if item["id"] == template_id),
#         None
#     )
#
#     if not template:
#         await callback.answer("Шаблон не найден", show_alert=True)
#         return
#
#     await save_filter(
#         state,
#         "template",
#         {
#             "id": template["id"],
#             "name": template["name"],
#         }
#     )
#     await callback.answer("Шаблон сохранён")
#     await show_filters_message(callback, state)
#
#
# @router.callback_query(ChecksMenuCb.filter(F.action == "apply"))
# async def apply_filters(callback: CallbackQuery, state: FSMContext):
#     filters = await get_filters(state)
#
#     payload = {
#         "section": "checks",
#         "filters": filters,
#     }
#
#     # Потом сюда можно будет добавить отправку payload на бекэнд.
#     # Сейчас только заглушка.
#     print(payload)
#
#     await callback.answer()
#     await callback.message.answer("Спасибо, что оставили сообщение!")