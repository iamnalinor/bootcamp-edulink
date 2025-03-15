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
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Format
from emoji import emojize

from app import config
from app.config import LOCALES
from app.misc import dp
from app.models import Container, User
from app.states import (
    ContainerCreateSG,
    ContainersSG,
    MainSG,
    RegisterSG,
    SettingsSG,
)
from app.utils import lazy_gettext as _
from app.utils import parse_ietf_tag
from app.widgets import Emojize

logger = logging.getLogger(__name__)


@dp.message(CommandStart())
async def start_cmd(
    message: types.Message, user: User, dialog_manager: DialogManager
) -> None:
    if user.lang_code is None:
        user.lang_code = parse_ietf_tag(message.from_user.language_code)
        await user.save()

        logger.debug("Language for user %d has been set to %s", user.id, user.lang_code)

        i18n = dialog_manager.middleware_data["i18n"]
        i18n.current_locale = user.lang_code

        locale = LOCALES[user.lang_code]
        await message.answer(
            emojize(
                _(
                    "Установлен язык {locale.flag} {locale.name}. "
                    "Ты можешь изменить его по команде /settings."
                ).format(locale=locale)
            )
        )

    if not user.registered:
        await dialog_manager.start(RegisterSG.fio, mode=StartMode.RESET_STACK)
        return

    await dialog_manager.start(
        MainSG.intro, mode=StartMode.RESET_STACK, show_mode=ShowMode.NO_UPDATE
    )
    dialog_manager.show_mode = ShowMode.SEND

    if message.text.startswith("/start cjoin_"):
        code = message.text[len("/start cjoin_") :]
        container = await Container.get(invite_code=code).prefetch_related(
            "owner", "participants"
        )
        if container:
            if user in [container.owner, *container.participants]:
                await message.answer(
                    _("Ты уже находишься в этом контейнере."), parse_mode=None
                )
            else:
                await message.answer(
                    _("Ты присоединился к контейнеру {container.name}!").format(
                        container=container
                    ),
                    parse_mode=None,
                )
                await container.participants.add(user)

            await dialog_manager.start(
                ContainersSG.view,
                {"container_id": container.id},
            )
            return
        await message.answer(_("Контейнер не найден."))

    await dialog_manager.show()


@dp.message(Command("show"))
@dp.callback_query(F.data == "show_menu")
async def show_cmd(__: types.Update, dialog_manager: DialogManager) -> None:
    await dialog_manager.show(ShowMode.SEND)


@dp.errors(
    ExceptionTypeFilter(
        UnknownIntent, OutdatedIntent, UnknownState, DialogStackOverflow
    )
)
async def error_handler(exception: types.Update, dialog_manager: DialogManager) -> None:
    logger.exception("Error in dialog manager for user")

    await dialog_manager.reset_stack()

    update = exception.update.message or exception.update.callback_query or None
    if update:
        await update.answer(_("Произошла ошибка. Пожалуйста, нажми /start"))


async def name_getter(
    user: User, event_from_user: types.User, **__: Any
) -> dict[str, Any]:
    try:
        name = user.name
    except Exception:
        logger.exception("Failed when getting user.name, falled back to first_name")
        name = event_from_user.first_name

    return {
        "first_name": name,
        "figma_url": config.FIGMA_URL,
    }


start_dialog = Dialog(
    Window(
        Format(
            _(
                "Привет, {first_name}!\n\n"
                "<a href='{figma_url}'>Открыть макет в Figma</a>"
            )
        ),
        Start(
            Emojize(_(":heavy_plus_sign: Новый контейнер")),
            "container_create",
            state=ContainerCreateSG.name,
        ),
        Start(
            Emojize(_(":package: Контейнеры")),
            "containers",
            state=ContainersSG.intro,
        ),
        Start(
            Emojize(_(":gear: Настройки")),
            "settings",
            state=SettingsSG.intro,
        ),
        state=MainSG.intro,
        getter=name_getter,
        disable_web_page_preview=True,
    ),
)
