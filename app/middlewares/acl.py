import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.models.user import User

logger = logging.getLogger(__name__)


class ACLMiddleware(BaseMiddleware):
    """
    Adds a User object to middleware data, creating DB record if user is not found.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if (event_user := data.get("event_from_user")) and "user" not in data:
            user = await User.get_or_none(id=event_user.id)
            if user is None:
                user = await User.create(id=event_user.id)
                logger.info(f"Created new user: {user} from {event}")
            data["user"] = user

        return await handler(event, data)
