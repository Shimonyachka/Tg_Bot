import aiohttp
import asyncio

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from config import config

main_router = Router()


@main_router.message(Command(commands='start', prefix='/'))
async def start_command(message: Message) -> None:
    welcome_text: str = "Привет"
    await message.answer(welcome_text)


@main_router.message(Command(commands="help", prefix="/"))
async def help_command(message: Message) -> None:
    text: str = "Чупапи муняню"
    await message.answer(text)


@main_router.message(Command(commands="facts"))
async def animals_command(message: Message) -> None:  
    api_key = config.deepseek_api_key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt: str = "Сгенерируй один интересный факт о каком-нибудь животном"

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    await message.answer(
                        text=result["choices"][0]["message"]["content"]
                    )
                else:
                    error_text = await response.text()
                    await message.answer(f"❌ Ошибка DeepSeek API: {response.status}\n{error_text}")                        
    except asyncio.TimeoutError:
        await message.answer("❌ Превышено время ожидания ответа от DeepSeek")
    except Exception as e:
        await message.answer(f"❌ Ошибка при обращении к DeepSeek: {str(e)}")
