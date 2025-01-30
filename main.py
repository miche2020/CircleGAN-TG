import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN, MODEL_PATH, LOG_LEVEL
from models.model_handler import StyleTransferModel
from bot.handlers import commands, images, callbacks
from bot.handlers.commands import set_commands

# Настраиваем логирование
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализируем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Загружаем модель
try:
    model_handler = StyleTransferModel(MODEL_PATH)
    model = model_handler.model
    logger.info("Модель успешно инициализирована")
except Exception as e:
    logger.error(f"Ошибка при инициализации модели: {str(e)}")
    raise

# Словарь для хранения изображений пользователей
user_images = {}

def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    # Команды
    dp.register_message_handler(commands.cmd_start, commands=['start', 'help'])
    dp.register_message_handler(lambda msg: commands.cmd_clear(msg, user_images), commands=['clear'])
    dp.register_message_handler(lambda msg: commands.cmd_check(msg, user_images), commands=['check'])

    # Обработка фото
    dp.register_message_handler(
        lambda msg: images.handle_photo(msg, user_images),
        content_types=['photo']
    )

    # Callback обработчики
    dp.register_callback_query_handler(
        lambda c: callbacks.process_style_transfer(c, user_images, model),
        lambda c: c.data.startswith('style_')
    )
    dp.register_callback_query_handler(
        lambda c: callbacks.clear_images_callback(c, user_images),
        lambda c: c.data.startswith('clear_')
    )
    dp.register_callback_query_handler(
        callbacks.retry_style_transfer,
        lambda c: c.data.startswith('retry_')
    )

async def on_startup(dp: Dispatcher):
    """Действия при запуске бота"""
    # Устанавливаем команды бота
    await set_commands(dp.bot)
    # Логируем, что бот запущен
    logger.info("Бот запущен")

async def on_shutdown(dp: Dispatcher):
    """Действия при остановке бота"""
    logger.info("Бот остановлен")
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()

if __name__ == '__main__':
    # Регистрируем обработчики
    register_handlers(dp)
    
    # Запускаем бота
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    ) 