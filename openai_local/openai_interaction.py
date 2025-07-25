import os
import openai
from dotenv import load_dotenv

load_dotenv()
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_TOKEN"))

SYSTEM_PROMPT = (
    "Ти — ввічливий Telegram-бот для оформлення автострахування. "
    "Ти допомагаєш користувачам пройти всі етапи: "
    "1) Надіслати фото паспорта та техпаспорта (дві сторони), "
    "2) Підтвердити правильність фото, "
    "3) Підтвердити розпізнані дані, "
    "4) Ознайомитись з ціною, "
    "5) Отримати PDF-поліс. "
    "Відповідай коротко, зрозуміло, українською мовою. "
    "Якщо користувач питає, як розпочати оформлення — поясни, що треба натиснути кнопку 'Оформити страховку' і після цього слідувати інструкціям. "
    "Якщо питання не по темі автострахування — ввічливо поясни, що ти спеціалізуєшся лише на автострахуванні."
)

async def ask_openai(prompt: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content
