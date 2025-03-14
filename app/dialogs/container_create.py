import datetime
import logging

from aiogram import types
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Next, Button, CalendarConfig, Calendar, Start
from aiogram_dialog.widgets.text import Const

from app.misc import BACK, BACK_STATE
from app.models import Container, User
from app.states import ContainerCreateSG, ContainersSG
from app.widgets import Emojize

logger = logging.getLogger(__name__)


async def container_name_filter(message: types.Message, user: User, *__):
    name_exists = await Container.filter(name=message.text, owner=user).exists()
    if name_exists:
        await message.answer(
            "Это имя уже занято. Попробуй добавить номер группы, дату или год обучения."
        )
        return False
    return True


async def container_create(__, ___, manager: DialogManager):
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
    __,
    manager: DialogManager,
    date: datetime.date,
):
    if date < datetime.date.today():
        await call.answer(
            "Нельзя выбирать дату в прошлом. Попробуй ещё раз.",
            show_alert=True,
        )
        return

    manager.dialog_data["deadline"] = date.isoformat()
    await manager.next()


container_create_dialog = Dialog(
    Window(
        Const("Создаём новый контейнер.\n\nВведи название:"),
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
        Const("Введи описание задания:"),
        TextInput("i_container_description", on_success=Next()),
        Next(Const("Пропустить")),
        BACK_STATE,
        state=ContainerCreateSG.description,
    ),
    Window(
        Emojize(
            ":calendar: Выбери срок задания. Дедлайн наступит в 23:59 МСК в этот день:"
        ),
        Calendar(
            id="location_date",
            on_click=deadline_selected,
            config=CalendarConfig(min_date=datetime.date(2025, 3, 1)),
        ),
        TextInput("i_container_deadline", on_success=Next()),
        Next(Const("Пропустить")),
        BACK_STATE,
        state=ContainerCreateSG.deadline,
    ),
    Window(
        Const("Всё готово! Нажми на кнопку, чтобы завершить создание."),
        Button(
            Emojize(":fire: Создать контейнер"),
            id="container_open",
            on_click=container_create,
        ),
        BACK_STATE,
        state=ContainerCreateSG.outro,
        preview_add_transitions=[Start(Const(""), "", ContainersSG.view)],
    ),
)
