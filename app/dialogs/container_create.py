import datetime
import logging
from typing import Any

from aiogram import types
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Calendar, CalendarConfig, Next, Start
from aiogram_dialog.widgets.text import Const

from app.misc import BACK, BACK_STATE
from app.models import Container, User
from app.states import ContainerCreateSG, ContainersSG
from app.utils import lazy_gettext as _
from app.widgets import Emojize

logger = logging.getLogger(__name__)


async def container_name_filter(message: types.Message, user: User, *__: Any) -> bool:
    name_exists = await Container.filter(name=message.text, owner=user).exists()
    if name_exists:
        await message.answer(
            _(
                "Это имя уже занято. Попробуй добавить номер группы, дату или год обучения."
            )
        )
        return False
    return True


async def container_create(
    __: types.CallbackQuery, ___: Button, manager: DialogManager
) -> None:
    user = manager.middleware_data["user"]
    deadline = manager.dialog_data.get("deadline")
    container = await Container.create(
        name=manager.find("i_container_name").get_value(),
        description=manager.find("i_container_description").get_value(),
        deadline=datetime.datetime.fromisoformat(deadline) if deadline else None,
        owner=user,
    )

    await manager.done(show_mode=ShowMode.NO_UPDATE)
    await manager.start(ContainersSG.view, {"container_id": container.id})


async def deadline_selected(
    call: types.CallbackQuery,
    __: Button,
    manager: DialogManager,
    date: datetime.date,
) -> None:
    if date < datetime.date.today():
        await call.answer(
            _("Нельзя выбирать дату в прошлом. Попробуй ещё раз."),
            show_alert=True,
        )
        return

    manager.dialog_data["deadline"] = date.isoformat()
    await manager.next()


container_create_dialog = Dialog(
    Window(
        Const(
            _(
                "Ты можешь хранить решения заданий в <b>контейнерах</b>. "
                "Одно задание на группу студентов — один контейнер.\n\n"
                "После создания можно поделиться ссылкой на контейнер, "
                "по которой студенты будут загружать решения.\n\n"
                "Введи название задания:"
            )
        ),
        BACK,
        TextInput(
            "i_container_name",
            filter=container_name_filter,
            on_success=Next(),
        ),
        state=ContainerCreateSG.name,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const(_("Введи описание задания:")),
        TextInput("i_container_description", on_success=Next()),
        Next(Const(_("Пропустить"))),
        BACK_STATE,
        state=ContainerCreateSG.description,
    ),
    Window(
        Emojize(
            _(
                ":calendar: Выбери срок задания. Дедлайн наступит в 23:59 МСК в этот день:"
            )
        ),
        Calendar(
            id="location_date",
            on_click=deadline_selected,
            config=CalendarConfig(min_date=datetime.date(2025, 3, 1)),
        ),
        TextInput("i_container_deadline", on_success=Next()),
        Next(Const(_("Пропустить"))),
        BACK_STATE,
        state=ContainerCreateSG.deadline,
    ),
    Window(
        Const(_("Всё готово! Нажми на кнопку, чтобы завершить создание.")),
        Button(
            Emojize(_(":fire: Создать контейнер")),
            id="container_open",
            on_click=container_create,
        ),
        BACK_STATE,
        state=ContainerCreateSG.outro,
        preview_add_transitions=[Start(Const(""), "", ContainersSG.view)],
    ),
)
