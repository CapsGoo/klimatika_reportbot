from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from datetime import datetime
from config import BOT_TOKEN
import os

# Инициализация логирования
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s",
    handlers=[
        logging.FileHandler(
            f"logs/logs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        ),
        logging.StreamHandler(),
    ],
)


users = {}  # Need replace with DB

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()  # DON'T USE IN FINAL VERSION OF PROJECT
dp = Dispatcher(storage=storage)


from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

# Создаем основной экземпляр i18n (как у вас сейчас)
i18n = I18n(path="locales", default_locale="en", domain="messages")

# Создаем отдельные экземпляры для PDF генерации
i18n_en = I18n(path="locales", default_locale="en", domain="messages")
i18n_ru = I18n(path="locales", default_locale="ru", domain="messages")

def on_startup(dp: Dispatcher):
    import src.handlers.message as message_handlers
    import src.handlers.callbacks as callback_handlers
    logging.debug("Bot is starting up...")

    dp.callback_query.middleware(SimpleI18nMiddleware(i18n=i18n))
    dp.message.middleware(SimpleI18nMiddleware(i18n=i18n))
    dp.include_router(message_handlers.users.users_router)
    dp.include_router(callback_handlers.users.users_router)

    logging.debug("Startup complete!")
    ...


async def on_shutdown():
    # Очистка ресурсов при завершении работы
    logging.debug("Shutting down the bot...")
    # Можно выполнить дополнительные действия для завершения работы
    await bot.close()
    logging.debug("Shutdown complete.")




