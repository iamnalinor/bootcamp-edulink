import logging
import operator
from datetime import timedelta
from typing import Any

from aiogram import types
from aiogram.types import User
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import (
    Next,
    ScrollingGroup,
    Select,
    Button,
)
from aiogram_dialog.widgets.text import Jinja, Format

from app.misc import BACK
from app.models import Homework, Container
from app.states import HomeworksSG
from app.widgets import Emojize

logger = logging.getLogger(__name__)


async def homeworks_getter(user: User, dialog_manager: DialogManager, **__):
    container_id = dialog_manager.start_data["container_id"]
    container = await Container.get(id=container_id).prefetch_related("owner")
    return {
        "container": container,
        "homeworks": await Homework.filter(container=container).prefetch_related(
            "owner"
        ),
    }


async def open_homework(__, ___, manager: DialogManager, homework_id: str):
    await manager.start(
        HomeworksSG.view, data=manager.start_data | {"homework_id": int(homework_id)}
    )


async def homework_view_getter(dialog_manager: DialogManager, **__) -> dict[str, Any]:
    container_id = dialog_manager.start_data["container_id"]
    container = await Container.get(id=container_id).prefetch_related("owner")
    homework_id = dialog_manager.start_data["homework_id"]
    homework = await Homework.get(id=homework_id).prefetch_related("owner", "container")

    created_at = (homework.created_at + timedelta(hours=3)).strftime(
        "%d.%m.%Y %H:%M:%S МСК"
    )

    return {
        "container": container,
        "homework": homework,
        "created_at": created_at,
    }


async def download_homework(
    call: types.CallbackQuery, __, manager: DialogManager
) -> None:
    homework_id = manager.start_data["homework_id"]
    homework = await Homework.get(id=homework_id)
    await call.message.answer_document(homework.file_id)
    await manager.show(ShowMode.SEND)


homeworks_dialog = Dialog(
    Window(
        Emojize(":package: <b>Доступные задания</b>"),
        ScrollingGroup(
            Select(
                Format("{item.owner.fio}"),
                id="s_homeworks",
                item_id_getter=operator.attrgetter("id"),
                items="homeworks",
                on_click=open_homework,
            ),
            id="scroll_homeworks",
            width=1,
            height=10,
            hide_on_single_page=True,
        ),
        BACK,
        state=HomeworksSG.intro,
        getter=homeworks_getter,
        preview_add_transitions=[Next()],
    ),
    Window(
        Emojize(
            Jinja("""
:package: Контейнер {{ container.name }} › Решение {{ homework.id }}
Отправил {{ homework.owner.fio }} в {{ created_at }}

{% if homework.text %}
<blockquote expandable>{{ homework.text }}</blockquote>
{% endif %}
""")
        ),
        Button(
            Emojize(":inbox_tray: Скачать"),
            "download_homework",
            download_homework,
        ),
        BACK,
        getter=homework_view_getter,
        state=HomeworksSG.view,
    ),
)
