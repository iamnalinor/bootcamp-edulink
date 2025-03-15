from typing import Any

import emoji
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Const


class Emojize(Const):
    """
    Emojize text using `emoji` library.
    Besides str, it can accept LazyProxy and Text objects as well.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    async def _render_text(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str:
        text = self.text
        if hasattr(text, "render_text"):
            text = await text.render_text(data, manager)

        return emoji.emojize(str(text), language="alias")
