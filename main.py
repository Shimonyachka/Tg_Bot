import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import config


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_routers()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
