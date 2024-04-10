import asyncio
import logging


from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bestsmmlike_venv.config_reader import config
from bestsmmlike_venv.bot_handlers import keyboard_router, ord_router


async def set_commands(bot: Bot):
    # Определение списка команд для бота
    commands = [
        BotCommand(command="/start", description="Начать"),
        BotCommand(command="/order", description="Перейти к оформлению заказа"),
        BotCommand(command="/order_status", description="Получить статус заказа")
    ]
    # Установка списка команд для бота
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(keyboard_router, ord_router)

    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
