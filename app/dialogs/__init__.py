"""
Dialogs (see aiogram_dialog), which are used in the process of working with the bot.
They are automatically imported from this directory.

Each file consists only of one dialog named the file name + "_dialog".
For example, "start.py" contains "start_dialog".

There may be additional function-handlers in the file.
They should be named as follows:
    - <name>_cmd for commands;
    - <name>_cb for callback queries;
    - <name>_handler for messages and other updates.

There is a logger instance in each file, named "logger".
"""

import importlib
from pathlib import Path

dialogs = []
for path in Path(__file__).parent.glob("*.py"):
    if path.stem == "__init__":
        continue
    module = importlib.import_module(f"app.dialogs.{path.stem}")
    assert hasattr(module, f"{path.stem}_dialog"), (
        f"Dialog {path.stem}_dialog not found in {path}"
    )
    dialogs.append(getattr(module, f"{path.stem}_dialog"))
