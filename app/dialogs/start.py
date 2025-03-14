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

from app.misc import dp
from app.models import User, Container
from app.states import (
    MainSG,
    RegisterSG,
    ContainersSG,
    ContainerCreateSG,
)
from app.widgets import Emojize

logger = logging.getLogger(__name__)


@dp.message(CommandStart())
async def start_cmd(message: types.Message, user: User, dialog_manager: DialogManager):
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
                await message.answer("Ты уже находишься в этом контейнере.")
            else:
                await message.answer(
                    f"Ты присоединился к контейнеру {container.name}!", parse_mode=None
                )
                await container.participants.add(user)

            await dialog_manager.start(
                ContainersSG.view,
                {"container_id": container.id},
            )
            return
        else:
            await message.answer("Контейнер не найден.")

    await dialog_manager.show()


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
        Format(
            "Привет, {first_name}!\n\n"
            "<a href='https://www.figma.com/proto/nIJ6EyZJLfZpVtuLm9qmT2/Untitled?page-id=0%3A1&node-id=1-545&p=f&viewport=-60%2C173%2C0.29&t=IshnLMZRA7KhXim3-1&scaling=min-zoom&content-scaling=fixed&starting-point-node-id=1%3A545'>Открыть макет в Figma</a>"
        ),
        Start(
            Emojize(":heavy_plus_sign: Новый контейнер"),
            "container_create",
            state=ContainerCreateSG.name,
        ),
        Start(
            Emojize(":package: Контейнеры"),
            "containers",
            state=ContainersSG.intro,
        ),
        state=MainSG.intro,
        getter=name_getter,
        disable_web_page_preview=True,
    ),
)
