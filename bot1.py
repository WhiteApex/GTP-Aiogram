import asyncio
import os
import re
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from mistralai import Mistral
from aiogram.enums import ParseMode

# Настройки
TELEGRAM_TOKEN = os.environ['TOKEN1']
MISTRAL_API_KEY = os.environ['API']
client = Mistral(api_key=MISTRAL_API_KEY) 


# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Функция для отправки запроса к API Mistral
async def run_mistral(user_message, model="mistral-small-latest"):
    messages = [{"role": "user", "content": user_message}]
    chat_response = client.chat.complete(model=model, messages=messages)
    return chat_response.choices[0].message.content

# Обработчик команды /start
@dp.message(Command(commands=['start']))
async def send_welcome(message: Message):
    await message.reply("Привет! Я бот, который может отвечать на ваши вопросы. Задайте мне вопрос!")

# Функция для форматирования кода
def format_code_in_text(text):
    # Регулярное выражение для поиска фрагментов кода
    code_pattern = re.compile(r'```(.*?)```', re.DOTALL)

    # Функция для замены найденных фрагментов кода
    def replace_code(match):
        code = match.group(1).strip()
        return f"```\n{code}\n```"

    # Заменяем все найденные фрагменты кода
    formatted_text = code_pattern.sub(replace_code, text)
    return formatted_text

# Функция для форматирования текста
def format_text(text):
    # Примеры форматирования
    text = text.replace("**", "*")  # Жирный шрифт
    text = text.replace("__", "_")  # Курсив
    text = text.replace("~~", "~")  # Зачеркнутый текст
    return text

# Обработчик текстовых сообщений
@dp.message()
async def handle_message(message: Message):
    user_message = message.text
    response = await run_mistral(user_message)
    formatted_response = format_text(response)
    formatted_response = format_code_in_text(formatted_response)

    await message.reply(formatted_response, parse_mode=ParseMode.MARKDOWN)

# Обработчик ошибок
@dp.errors()
async def error_handler(update: types.Update, exception: Exception):
    logging.error(f'Update "{update}" caused error "{exception}"')

    
async def main():
    print("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
