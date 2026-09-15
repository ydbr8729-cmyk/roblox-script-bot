import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from google import genai

# Токены
TELEGRAM_TOKEN = "8605250509:AAFFfCEwfLxgOd5sX-wcofGfpVyphP_XR7I"
GEMINI_API_KEY = "AQ.Ab8RN6Jd7wpV88Kky13gucDlk7zRZKEx5KDBb8U1nhdPgcQovA"

# Инициализация клиентов
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Обновленный системный промпт с жирной инструкцией и ссылкой на топчик
SYSTEM_INSTRUCTION = (
    "Ты — продвинутый ИИ-ассистент для написания Luau-скриптов под Roblox-экзекьюторы. "
    "Пользователь просит тебя написать скрипт. "
    "Выдавай рабочий код на Luau в блоке кода (markdown). "
    "💎 **Обязательно добавляй после кода инструкцию по запуску строго в таком стиле с эмодзи:**\n\n"
    "🚀 **Инструкция по запуску:**\n"
    "1️⃣ Скачай топовый экзекьютор **Xeno** по ссылке: [🔗 Клик сюда](https://www.xeno.now/download)\n"
    "2️⃣ Инжекти его в Роблокс перед запуском скрипта.\n"
    "3️⃣ Скопируй код выше, закинь в экзекьютор и жми Execute. Погнали фармить соляру!\n\n"
    "Используй актуальные функции экзекьюторов (getgenv, fireclickdetector и т.д.)."
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Здаров. Закинь мне идею скрипта (например: «сделай автофарм сундуков» или «телепорт по клику»), "
        "и я выдам готовый Luau-код под экзекьютор вместе с инструкцией."
    )

@dp.message(F.text)
async def generate_script(message: types.Message):
    waiting_msg = await message.answer("Ковыряюсь в коде, секунду...")
    
    try:
        response = ai_client.models.generate_content(
            model="gemini-3.5-flash",
            contents=message.text,
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
            }
        )
        
        reply_text = response.text
        
        # Удаляем ждущее сообщение
        await bot.delete_message(chat_id=message.chat.id, message_id=waiting_msg.message_id)
        
        # Режем простыню текста на куски под лимит Телеграма
        max_length = 4000
        for i in range(0, len(reply_text), max_length):
            chunk = reply_text[i:i + max_length]
            await message.answer(chunk, parse_mode="Markdown")
        
    except Exception as e:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=waiting_msg.message_id,
            text=f"Бля, ошибка при генерации: {e}"
        )

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен и ждет работяг...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
