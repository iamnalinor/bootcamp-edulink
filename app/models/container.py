import random
import string

from tortoise import Model, fields


def rnd_id() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))


class Container(Model):
    id = fields.IntField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    invite_code = fields.TextField(default=rnd_id)
    owner = fields.ForeignKeyField("models.User", related_name="containers_owner")
    name = fields.TextField()
    is_archived = fields.BooleanField(default=False)
    description = fields.TextField(null=True)
    deadline = fields.DatetimeField(null=True)
    participants = fields.ManyToManyField(
        "models.User", related_name="container_participants"
    )
