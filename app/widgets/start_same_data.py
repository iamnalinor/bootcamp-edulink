from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Start


class StartWithSameData(Start):
    """
    Acts like Start, but copies start_data from the previous dialog.
    """

    async def _on_click(
        self,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        if self.user_on_click:
            await self.user_on_click(callback, self, manager)

        start_data = (manager.start_data or {}) | (self.start_data or {})
        await manager.start(self.state, start_data, self.mode)
