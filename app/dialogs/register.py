import logging
import re

from aiogram import types
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next
from aiogram_dialog.widgets.text import Const

from app.misc import HOME
from app.states import RegisterSG
from app.utils import lazy_gettext as _
from app.utils import maybe_next
from app.widgets import Emojize

logger = logging.getLogger(__name__)


async def save_fio(
    message: types.Message, __: MessageInput, manager: DialogManager
) -> None:
    fio = message.text
    if len(fio.split()) < 2 or not re.fullmatch(r"[а-яА-ЯёЁ\w ]+", fio):
        await message.answer("Некорректное ФИО.")
        return

    user = manager.middleware_data["user"]
    await user.update_from_dict({"fio": fio.title()}).save()

    await maybe_next(manager)


register_dialog = Dialog(
    Window(
        Const(
            _(
                "Добро пожаловать в EduLink!\n\n"
                "Введи своё ФИО. Пример: Иванов Иван Иванович"
            )
        ),
        MessageInput(save_fio, ContentType.TEXT),
        state=RegisterSG.fio,
        preview_add_transitions=[Next()],
    ),
    Window(
        Emojize(_(":party_popper: Ты зарегистрировался!")),
        HOME,
        state=RegisterSG.outro,
    ),
)
