"""
Utility functions.
"""

import random
import string
from collections.abc import Coroutine

from aiogram import types
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.widget_event import ensure_event_processor


def rnd_id() -> str:
    """
    Generates a random 10-character string.
    :return: Random string consisting of letters and digits.
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))


def escape(text: str) -> str:
    """
    Escapes HTML text.
    :param text: Unsafe text
    :return: Safe text that can be included into HTML markup.
    """
    return text.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")


@ensure_event_processor
async def on_error(message: types.Message, *__) -> None:
    """
    Event processor for invalid inputs.
    :param message: Message to be answered
    :param __:
    """
    await message.answer("Неверный ввод. Попробуй ещё раз.")


def maybe_next(manager: DialogManager) -> Coroutine[None, None, None]:
    """
    Either switch to the next state or mark the window as done.
    :param manager:
    :return:
    """
    if "single" in (manager.start_data or {}):
        return manager.done()

    return manager.next()
