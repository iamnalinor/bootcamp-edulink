import datetime
import io
import logging
import operator
import re
from typing import Any

import PyPDF2
from aiogram import F, Bot, types
from aiogram.types import User, BufferedInputFile
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Next,
    ScrollingGroup,
    Select,
    Button,
)
from aiogram_dialog.widgets.text import Const, Jinja, Case, Format
from tortoise.expressions import Q

from app import config
from app.misc import BACK
from app.models import Container, Homework
from app.services.gpt import summarize_homework_text
from app.states import ContainersSG, HomeworksSG
from app.utils import get_short_fio
from app.widgets import Emojize, StartWithSameData

logger = logging.getLogger(__name__)


async def containers_getter(user: User, **__):
    return {
        "containers": await Container.filter(
            (Q(owner=user) | (Q(participants=user) & ~Q(is_archived=True)))
        ).prefetch_related("owner"),
    }


async def open_container(__, ___, manager: DialogManager, container_id: str):
    await manager.start(ContainersSG.view, data={"container_id": int(container_id)})


async def container_view_getter(
    dialog_manager: DialogManager, bot: Bot, user: User, **__
) -> dict[str, Any]:
    container_id = dialog_manager.start_data["container_id"]
    container = await Container.get(id=container_id).prefetch_related("owner")

    me = await bot.me()
    return {
        "container": container,
        "is_owner": container.owner.id == user.id,
        "homework_sent": await Homework.get_or_none(container=container, owner=user),
        "invite_link": f"https://t.me/{me.username}?start=cjoin_{container.invite_code}",
    }


async def archive_container(__, ___, manager: DialogManager) -> None:
    container_id = manager.start_data["container_id"]
    container = await Container.get(id=container_id)
    await container.update_from_dict({"is_archived": True}).save()
    await manager.back()


async def homework_handler(message: types.Message, __, manager: DialogManager) -> None:
    if message.document and message.document.file_size > (5 * 1024 * 1024):
        await message.answer("Размер файла должен быть не больше 5 МБ.")
        return

    parts = message.document.file_name.rsplit(".", maxsplit=1)
    if len(parts) == 1:
        await message.answer("Неверное имя файла.")
        return

    file_name, file_ext = parts
    file_ext = file_ext.lower()

    bot: Bot = manager.middleware_data["bot"]
    user = manager.middleware_data["user"]

    await message.answer("Обработка...\n\nЭто займет до 30 секунд.")

    f = io.BytesIO()
    await bot.download(message.document.file_id, f)

    match file_ext:
        case "pdf":
            pdf_reader = PyPDF2.PdfReader(f)
            text = "".join([page.extract_text() for page in pdf_reader.pages])
            title = "_" + await summarize_homework_text(text)
        case _:
            title = re.sub(r"[\s\-]", "-", re.sub(r"[^a-zA-Z0-9\s_\-]", "", file_name))

    name = (
        get_short_fio(user.fio)
        + "_"
        + datetime.datetime.now().strftime("%d_%m")
        + title
        + "."
        + parts[-1]
    )
    f.seek(0)
    sent = await bot.send_document(
        config.UPLOAD_FILES_CHAT_ID,
        BufferedInputFile(f.read(), filename=name),
    )

    homework = await Homework.create(
        owner=manager.middleware_data["user"],
        container=await Container.get(id=manager.start_data["container_id"]),
        text=message.text,
        file_id=sent.document.file_id,
        name=name,
    )
    await message.answer(f"Отправлено! ID решения — <code>{homework.id}</code>")
    await manager.done()


containers_dialog = Dialog(
    Window(
        Emojize(":package: <b>Доступные контейнеры</b>"),
        ScrollingGroup(
            Select(
                Case(
                    {
                        True: Emojize(Format("{item.name} :gear:")),
                        False: Format("{item.name}"),
                    },
                    selector=F["item"].owner.id
                    == F["event_from_user"].id,  # todo: gear for is_owner
                ),
                id="s_containers",
                item_id_getter=operator.attrgetter("id"),
                items="containers",
                on_click=open_container,
            ),
            id="scroll_containers",
            width=1,
            height=10,
            hide_on_single_page=True,
        ),
        BACK,
        state=ContainersSG.intro,
        getter=containers_getter,
        preview_add_transitions=[Next()],
    ),
    Window(
        Emojize(
            Jinja("""
:package: <b>Контейнер {{ container.name }}</b> › Просмотр
{% if container.is_archived %}:lock: Архивирован
{% elif container.deadline %}Дедлайн <b>{{ container.deadline.strftime('%d.%m.%Y') }} 23:59 МСК</b>
{% endif %}

{% if container.description %}<blockquote expandable>{{ container.description }}</blockquote>

{% endif %}
{% if homework_sent %}:white_check_mark: Отправлено решение под ID <code>{{ homework_sent.id }}</code>
{% endif %}
""")
        ),
        StartWithSameData(
            Emojize(":heavy_plus_sign: Загрузить решение"),
            "add_homework",
            state=ContainersSG.add_homework,
            when=~F["container"].is_archived & ~F["homework_sent"],
        ),
        StartWithSameData(
            Emojize(":mailbox_with_mail: Решения"),
            "homeworks_list",
            state=HomeworksSG.intro,
            when=F["is_owner"],
        ),
        StartWithSameData(
            Emojize(":link: Поделиться ссылкой"),
            "share_link",
            state=ContainersSG.share_link,
            when=F["is_owner"],
        ),
        StartWithSameData(
            Emojize(":lock: Архивировать"),
            id="archive_container",
            state=ContainersSG.confirm_archive,
            when=~F["container"].is_archived & F["is_owner"],
        ),
        BACK,
        getter=container_view_getter,
        state=ContainersSG.view,
    ),
    Window(
        Jinja(
            "Присоединиться к контейнеру {{ container.name }} можно по ссылке:\n\n"
            "{{ invite_link }}"
        ),
        BACK,
        getter=container_view_getter,
        state=ContainersSG.share_link,
    ),
    Window(
        Emojize(
            Jinja(
                ":warning: Ты хочешь архивировать контейнер <b>{{ container.name }}</b>. "
                "Он будет скрыт у студентов.\n\n"
                "Ты уверен? Это действие нельзя отменить."
            )
        ),
        Button(
            Const("Да, я уверен"),
            id="confirm_archive",
            on_click=archive_container,
        ),
        BACK,
        getter=container_view_getter,
        state=ContainersSG.confirm_archive,
    ),
    Window(
        Emojize(":memo: Отправь решение задания текстом или файлом до 5 МБ."),
        MessageInput(homework_handler),
        BACK,
        state=ContainersSG.add_homework,
    ),
)
