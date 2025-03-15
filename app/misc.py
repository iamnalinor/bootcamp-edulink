from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from aiogram_dialog import StartMode
from aiogram_dialog.widgets.kbd import Back, Cancel, Start
from aiogram_dialog.widgets.text import Const
from pyrogram import Client

from app.config import BOT_TOKEN, DEFAULT_LOCALE, REDIS_URL
from app.states import MainSG
from app.utils import lazy_gettext as _
from app.widgets import Emojize

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(
    storage=RedisStorage.from_url(
        REDIS_URL, key_builder=DefaultKeyBuilder(with_destiny=True)
    )
    if REDIS_URL
    else MemoryStorage()
)
_client: Client | None = None

i18n = I18n(path="locales/", default_locale=DEFAULT_LOCALE.lang_code)

BACK = Cancel(Const(_("‹ Назад")))
BACK_STATE = Back(Const("‹ Назад"))
CANCEL = Back(Const("‹ Отмена"))
HOME = Start(
    Emojize(_(":house: Домой")),
    id="go_home",
    state=MainSG.intro,
    mode=StartMode.RESET_STACK,
)


def get_client() -> Client:
    return _client


def set_client(client2: Client) -> None:
    global _client
    _client = client2
