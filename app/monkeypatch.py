"""
Monkeypatching aiogram, aiogram_dialog libraries.
Aiogram* have bad support for LazyProxy, mostly due to pydantic incompatibility.

The following changes are made:
1. Get the inner value of LazyProxy when initializing TelegramObject and TelegramMethod.
2. Cast Union[str, LazyProxy[str]] to str when rendering Text widget.
3. Cast self.template_text to str when initializing Jinja widget.
"""

from aiogram.methods.base import TelegramMethod
from aiogram.types.base import TelegramObject
from aiogram_dialog.widgets.text.base import Text
from aiogram_dialog.widgets.text.jinja import (
    JINJA_ENV_FIELD,
    Jinja,
    default_env,
)
from babel.support import LazyProxy


class CustomTelegramMethod(TelegramMethod):  # noqa
    def __init__(self, /, **kwargs):
        if LazyProxy is not None:
            for key, value in kwargs.items():
                if isinstance(value, LazyProxy):
                    kwargs[key] = value.value

        super(TelegramMethod, self).__init__(**kwargs)


class CustomTelegramObject(TelegramObject):
    def __init__(self, /, **kwargs):
        if LazyProxy is not None:
            for key, value in kwargs.items():
                if isinstance(value, LazyProxy):
                    kwargs[key] = value.value

        super(TelegramObject, self).__init__(**kwargs)


TelegramObject.__init__ = CustomTelegramObject.__init__
TelegramObject.__pydantic_base_init__ = True
TelegramMethod.__init__ = CustomTelegramMethod.__init__
TelegramMethod.__pydantic_base_init__ = True


async def text_render_text(self, data, manager) -> str:
    if not self.is_(data, manager):
        return ""

    return str(await self._render_text(data, manager))  # <<<<< Cast to str


Text.render_text = text_render_text


async def jinja_render_text(self, data, manager) -> str:
    if JINJA_ENV_FIELD in manager.middleware_data:
        env = manager.middleware_data[JINJA_ENV_FIELD]
    else:
        bot = manager.middleware_data.get("bot")
        env = getattr(bot, JINJA_ENV_FIELD, default_env)
    template = env.get_template(str(self.template_text))  # <<<<< Cast to str

    if env.is_async:
        return await template.render_async(data)
    return template.render(data)


Jinja._render_text = jinja_render_text
