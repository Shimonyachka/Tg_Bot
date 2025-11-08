from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

main_router = Router()


@main_router.message(Command(commands='start', prefix='/'))
async def start_command(message: Message) -> None:
    welcome_text: str = "Привет"
    await message.answer(welcome_text)