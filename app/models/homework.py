from tortoise import Model, fields


class Homework(Model):
    id = fields.IntField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    owner = fields.ForeignKeyField("models.User")
    container = fields.ForeignKeyField("models.Container")
    name = fields.TextField()
    text = fields.TextField(null=True)
    file_id = fields.TextField()
    mark = fields.IntField(null=True)
