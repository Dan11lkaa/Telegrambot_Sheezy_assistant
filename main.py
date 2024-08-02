from aiogram import Bot, Dispatcher
import asyncio
from config import TOKEN
from handlers import router
from aiogram.types import BotCommandScopeDefault
from keyboard import commands
from models import async_main
async def main():
    await async_main()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router=router)
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот отключен')
