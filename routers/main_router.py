import aiohttp
import uuid

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state

from config import config
from Utils.keyboard import main_menu_keyboard


main_router = Router()


class generation(StatesGroup):
    wait_answer = State()
    generate = State()


@main_router.message(Command(commands='start', prefix='/'))
async def start_command(message: Message) -> None:
    welcome_text: str = """
Привет☀️! 
Этот бот позволит вам узнать интересные факты о любом интересующем вас животном!🙉
Не стесняйтесь узнавать о любом животном, наш бот знает обо всех!🤓
"""
    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )


@main_router.message(F.text == "ℹ️ Помощь")
async def help_command(message: Message) -> None:
    text: str = "Кнопка '🐶 Факты' - Позволяет узнать что-то интересное про любое животное!"
    await message.answer(text)


@main_router.message(F.text == "🐶 Факты", StateFilter(default_state))
async def animals_command(message: Message, state: FSMContext) -> None:  
    await message.answer("Напиши, про какое животное ты хочешь узнать?")
    await state.set_state(generation.wait_answer)


@main_router.message(F.text, StateFilter(generation.wait_answer))
async def waiting_answer(message: Message, state: FSMContext) -> None: 
    wait_message = await message.answer("Твой факт уже почти готов...")

    save_animal = await generate_answer_gigachat(message.text)

    await wait_message.delete()
    await message.answer(save_animal)
    await state.set_state(default_state)


async def get_gigachat_token(auth_key: str, scope: str) -> str:
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    payload={
        'scope': scope
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {auth_key}'
    }
        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, ssl=False) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['access_token']
                else:
                    error_text = await response.text()
                    raise Exception(f"Не удалось получить токен: {response.status}. Ошибка: {error_text}")
    except Exception as e:
        raise Exception(f"Ошибка при запросе токена: {e}")


async def generate_answer_gigachat(prompt: str) -> str:
    try:
        access_token = await get_gigachat_token(
            config.gigachat_api_key.get_secret_value(),
            "GIGACHAT_API_PERS"    
        )

        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        system_prompt = """
Ты - профессиональный зоолог и знаешь много интересных фактов о животных. 
Создавай факты о животных, причем если тебя просят написать факт не о животном, то напиши, что
это не животное, укажите, пожалуйста, животное:
- Привлекательным заголовком с эмодзи
- Структурированным текстом с абзацами
- Эмодзи для визуального разделения
- Длиной 100 слов
"""
        
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Напиши пост на тему: {prompt}"
                }
            ],
            "stream": False,
            "repetition_penalty": 1.1,
            "max_tokens": 1024
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, ssl=False) as response:
                if response.status == 200:
                    result = await response.json()
                    generated_text = result['choices'][0]['message']['content']
                    return generated_text
                else:
                    error_text = await response.text()
                    return "❌ Извините, произошла ошибка при генерации поста. Попробуйте еще раз."
                    
    except Exception as e:
        return f"Ошибка: {str(e)}"

