"""
FSM states, describing window transitions.

The format is as follows:
    <name>SG
    <name> - human-readable name of group (can match the file name) in UpperCamelCase.
    Example: MainSG

The first state of a group is usually named "intro". Exception can be made
for a subgroup waiting for some user input.
If needed, the last state is always named "outro".
"""

from aiogram.fsm.state import State, StatesGroup


class RegisterSG(StatesGroup):
    fio = State()
    outro = State()


class MainSG(StatesGroup):
    intro = State()
