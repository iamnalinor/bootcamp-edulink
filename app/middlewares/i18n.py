from typing import TYPE_CHECKING, Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import SimpleI18nMiddleware

if TYPE_CHECKING:
    from app.models import User


class DatabaseI18nMiddleware(SimpleI18nMiddleware):
    """
    Retrieves the user's language from the database.
    If empty, falls back to the lang_code parameter from Telegram and saves it to the database.
    """

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        user: User = data["user"]
        return user.lang_code
