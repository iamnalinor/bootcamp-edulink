import logging
from typing import Any

from aiogram import F, types
from aiogram.filters import Command, CommandStart, ExceptionTypeFilter
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.api.exceptions import (
    DialogStackOverflow,
    OutdatedIntent,
    UnknownIntent,
    UnknownState,
)
from aiogram_dialog.widgets.text import Format

from app.misc import dp
from app.models import User
from app.states import (
    MainSG,
    RegisterSG,
)

logger = logging.getLogger(__name__)


@dp.message(CommandStart())
async def start_cmd(message: types.Message, user: User, dialog_manager: DialogManager):
    if not user.registered:
        await dialog_manager.start(RegisterSG.fio, mode=StartMode.RESET_STACK)
        return

    await dialog_manager.start(MainSG.intro, mode=StartMode.RESET_STACK)


@dp.message(Command("show"))
@dp.callback_query(F.data == "show_menu")
async def show_cmd(update, dialog_manager: DialogManager):
    await dialog_manager.show(ShowMode.SEND)


@dp.errors(
    ExceptionTypeFilter(
        UnknownIntent, OutdatedIntent, UnknownState, DialogStackOverflow
    )
)
async def error_handler(exception: types.Update, dialog_manager: DialogManager):
    logger.exception("Error in dialog manager for user")

    await dialog_manager.reset_stack()

    update = exception.update.message or exception.update.callback_query or None
    if update:
        await update.answer("Произошла ошибка. Пожалуйста, нажми /start")


async def name_getter(user: User, event_from_user: types.User, **_) -> dict[str, Any]:
    return {
        "first_name": user.fio.split()[1] or event_from_user.first_name,
    }


start_dialog = Dialog(
    Window(
        Format("Привет, {first_name}!"),
        state=MainSG.intro,
        getter=name_getter,
    ),
)
