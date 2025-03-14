import os
from envparse import env

env.read_envfile()
BOT_TOKEN = env.str("BOT_TOKEN")
UPLOAD_FILES_CHAT_ID = env.int("UPLOAD_FILES_CHAT_ID")
YANDEX_API_KEY = env.str("YANDEX_API_KEY")
YANDEX_FOLDER_ID = env.str("YANDEX_FOLDER_ID")

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
