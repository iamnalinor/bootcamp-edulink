import aiohttp

from app import config


async def summarize_homework_text(text: str) -> str:
    gpt_model = "yandexgpt-lite"

    body = {
        "modelUri": f"gpt://{config.YANDEX_FOLDER_ID}/{gpt_model}",
        "completionOptions": {"stream": False, "temperature": 0, "maxTokens": 4000},
        "messages": [
            {
                "role": "system",
                "text": "Ты получаешь на вход текст домашней работы студента. Классифицируй домашние работы в подходящую категорию по принципу: предмет, тема. В ответе укажи только предмет и тему через зяпятую. Пример вывода номер 1: 'Искусственный интеллект, Свертончные нейронные сети'. Пример вывода номер 2: 'Биология, Генетика'. Пример вывода номер 3: 'Геометрия, Стереометрия'. Выводи строго не больше 3 слов.",
            },
            {"role": "user", "text": text},
        ],
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {config.YANDEX_API_KEY}",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, json=body) as resp:
            operation_id = (await resp.json())["id"]

        url = f"https://llm.api.cloud.yandex.net/operations/{operation_id}"

        for _ in range(60):
            async with session.get(url) as resp:
                response = await resp.json()
                if response["done"]:
                    break
        else:
            raise RuntimeError(
                f"timeout waiting for response for operation {operation_id}"
            )

    answer = response["response"]["alternatives"][0]["message"]["text"]
    return " ".join([i.strip() for i in answer.split(",")]).replace(" ", "_")
