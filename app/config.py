import os
from collections import namedtuple

from envparse import env

env.read_envfile()
BOT_TOKEN = env.str("BOT_TOKEN")
REDIS_URL = env.str("REDIS_URL", "")
UPLOAD_FILES_CHAT_ID = env.int("UPLOAD_FILES_CHAT_ID")
YANDEX_API_KEY = env.str("YANDEX_API_KEY")
YANDEX_FOLDER_ID = env.str("YANDEX_FOLDER_ID")
API_ID = env.int("API_ID")
API_HASH = env.str("API_HASH")

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

Locale = namedtuple("Locale", ["lang_code", "flag", "name"])
LOCALES = {
    "en": Locale("en", ":United_States:", "English"),
    "ru": Locale("ru", ":Russia:", "Русский"),
}
DEFAULT_LOCALE = LOCALES["en"]

FIGMA_URL = "https://www.figma.com/proto/nIJ6EyZJLfZpVtuLm9qmT2/Untitled?page-id=0%3A1&node-id=1-545&p=f&viewport=-60%2C173%2C0.29&t=IshnLMZRA7KhXim3-1&scaling=min-zoom&content-scaling=fixed&starting-point-node-id=1%3A545"
FILE_SIZE_LIMIT_MB = 5
