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


class SettingsSG(StatesGroup):
    intro = State()
    choose_lang = State()


class ContainerCreateSG(StatesGroup):
    name = State()
    description = State()
    deadline = State()
    outro = State()


class ContainersSG(StatesGroup):
    intro = State()
    view = State()
    share_link = State()
    add_homework = State()
    confirm_archive = State()


class HomeworksSG(StatesGroup):
    intro = State()
    view = State()
