import re

from tortoise import Model, fields


class User(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    lang_code = fields.CharField(max_length=2, null=True)
    fio = fields.TextField(null=True)
    lang_code = fields.CharField(max_length=2, null=True)

    def __str__(self):
        return f"User #{self.id} {self.fio or ''}"

    @property
    def name(self) -> str:
        parts = self.fio.split()
        if re.fullmatch(r"[а-яА-ЯёЁ ]+", self.fio):
            return parts[1]
        return parts[0]

    @property
    def registered(self) -> bool:
        return bool(self.fio)
