import logging
import operator
from typing import Any

from aiogram import types
from aiogram.filters import Command
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Column, Radio, Start
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.widget_event import SimpleEventProcessor

from app.config import DEFAULT_LOCALE, LOCALES
from app.misc import BACK, dp
from app.models import User
from app.states import SettingsSG
from app.utils import lazy_gettext as _
from app.widgets import Emojize

logger = logging.getLogger(__name__)


@dp.message(Command("settings"))
async def settings_cmd(
    message: types.Message,
    dialog_manager: DialogManager,
) -> None:
    if dialog_manager.current_context().state in SettingsSG:
        await dialog_manager.show()
        return

    await dialog_manager.start(SettingsSG.intro)


async def locales_getter(
    dialog_manager: DialogManager, user: User, **__: Any
) -> dict[str, Any]:
    lang_code = user.lang_code or DEFAULT_LOCALE

    radio = dialog_manager.find("r_locales")
    await radio.set_checked(lang_code)

    return {"locales": LOCALES.values()}


async def set_lang_code(
    __: types.CallbackQuery,
    ___: Button,
    dialog_manager: DialogManager,
    lang_code: str,
) -> None:
    user: User = dialog_manager.middleware_data["user"]
    user.lang_code = lang_code
    await user.save()

    i18n = dialog_manager.middleware_data["i18n"]
    i18n.current_locale = lang_code

    logger.debug("Language for user %d has been set to %s", user.id, user.lang_code)


settings_dialog = Dialog(
    Window(
        Emojize(_(":gear: Настройки")),
        Start(
            Emojize(_(":white_flag: Изменить язык")),
            id="change_lang",
            state=SettingsSG.choose_lang,
        ),
        BACK,
        state=SettingsSG.intro,
    ),
    Window(
        Emojize(_(":white_flag: Выбери язык:")),
        Column(
            Radio(
                Emojize(Format("• {item[1]} {item[2]} •")),
                Emojize(Format("{item[1]} {item[2]}")),
                id="r_locales",
                item_id_getter=operator.itemgetter(0),
                items="locales",
                on_state_changed=SimpleEventProcessor(set_lang_code),
            ),
        ),
        BACK,
        getter=locales_getter,
        state=SettingsSG.choose_lang,
    ),
)
