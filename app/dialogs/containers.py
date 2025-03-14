import logging
import operator
from typing import Any

from aiogram import F, Bot, types
from aiogram.types import User
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

from app.misc import BACK
from app.models import Container, Homework
from app.states import ContainersSG, HomeworksSG
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

    homework = await Homework.create(
        owner=manager.middleware_data["user"],
        container=await Container.get(id=manager.start_data["container_id"]),
        text=message.text,
        file_id=message.document.file_id if message.document else None,
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
            when=~F["container"].is_archived & ~F["is_owner"] & ~F["homework_sent"],
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
