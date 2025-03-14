import logging
import operator

from aiogram import F, Bot
from aiogram.types import User
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import (
    Next,
    ScrollingGroup,
    Select,
    Button,
)
from aiogram_dialog.widgets.text import Const, Jinja, Case, Format
from tortoise.expressions import Q

from app.misc import BACK
from app.models import Container
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


async def container_view_getter(dialog_manager: DialogManager, bot: Bot, **__):
    container_id = dialog_manager.start_data["container_id"]
    container = await Container.get(id=container_id).prefetch_related("owner")

    user = dialog_manager.middleware_data["user"]
    me = await bot.me()
    return {
        "container": container,
        "is_owner": container.owner.id == user.id,
        "invite_link": f"https://t.me/{me.username}?start=cjoin_{container.invite_code}",
    }


async def archive_container(__, ___, manager: DialogManager):
    container_id = manager.start_data["container_id"]
    container = await Container.get(id=container_id)
    await container.update_from_dict({"is_archived": True}).save()
    await manager.back()


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
""")
        ),
        StartWithSameData(
            Emojize(":heavy_plus_sign: Загрузить решение"),
            "add_homework",
            state=ContainersSG.add_homework,
            when=~F["container"].is_archived & ~F["is_owner"],
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
)
