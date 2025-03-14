import random
import string

from tortoise import Model, fields


def rnd_id() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))


class Homework(Model):
    id = fields.IntField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    owner = fields.ForeignKeyField("models.User")
    container = fields.ForeignKeyField("models.Container")
