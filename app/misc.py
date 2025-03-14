from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import StartMode
from aiogram_dialog.widgets.kbd import Back, Cancel, Start
from aiogram_dialog.widgets.text import Const

from app.config import BOT_TOKEN
from app.states import MainSG
from app.widgets import Emojize

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

BACK = Cancel(Const("‹ Назад"))
BACK_STATE = Back(Const("‹ Назад"))
CANCEL = Back(Const("‹ Отмена"))
HOME = Start(
    Emojize(":house: Домой"),
    id="go_home",
    state=MainSG.intro,
    mode=StartMode.RESET_STACK,
)
