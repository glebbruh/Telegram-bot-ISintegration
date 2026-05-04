from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from bot.services.auth_help import AuthStates
from bot.keyboards.callbacks import LogoutConfirmCb
from bot.keyboards.menu import logout_confirm_keyboard

router = Router()

@router.message(F.text == "Выйти из аккаунта")
async def ask_logout_confirmation(message: Message):
    await message.answer(
        "Уверены ли вы, что хотите выйти из аккаунта?",
        reply_markup=logout_confirm_keyboard()
    )

@router.callback_query(LogoutConfirmCb.filter(F.action == "cancel"))
async def cancel_logout(callback: CallbackQuery):
    await callback.answer("Выход отменён")
    try:
        await callback.message.delete()
    except Exception:
        pass

@router.callback_query(LogoutConfirmCb.filter(F.action == "yes"))
async def confirm_logout(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        "Вы вышли из аккаунта.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AuthStates.waiting_for_email)
    await callback.message.answer("Для входа в бот введите ваш email")