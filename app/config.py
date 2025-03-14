import os
from envparse import env

env.read_envfile()
BOT_TOKEN = env.str("BOT_TOKEN")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite://db.sqlite3")

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        },
    },
}
