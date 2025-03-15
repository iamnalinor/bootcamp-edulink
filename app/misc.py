from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n import I18n
from aiogram_dialog import StartMode
from aiogram_dialog.widgets.kbd import Back, Cancel, Start
from aiogram_dialog.widgets.text import Const

from app.config import BOT_TOKEN, DEFAULT_LOCALE
from app.states import MainSG
from app.utils import lazy_gettext as _
from app.widgets import Emojize

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

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
