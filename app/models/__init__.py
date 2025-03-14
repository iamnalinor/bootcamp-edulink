"""
Database ORM models.

Warning: you should not import any aiogram objects here, including other modules that import aiogram objects.
Aiogram imports and installs uvloop, which is not compatible with aerich (migration tool used).
See https://github.com/tortoise/aerich/issues/129.
"""

from app.models.container import Container
from app.models.homework import Homework
from app.models.user import User

__all__ = ["Container", "Homework", "User"]
