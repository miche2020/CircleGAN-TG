from aiogram import types
from bot.keyboards import get_restart_keyboard
from aiogram.types import BotCommand

async def cmd_start(message: types.Message):
    welcome_text = """
    Привет! Я бот для переноса стиля. Вот мои команды:
    
    /start - показать это сообщение
    /help - показать это сообщение
    /check - проверить загруженные изображения
    /clear - очистить загруженные изображения
    
    Чтобы начать, отправьте мне два изображения:
    1. Изображение контента (то, что хотите стилизовать)
    2. Изображение стиля (откуда брать стиль)
    """
    await message.reply(welcome_text)

async def cmd_help(message: types.Message):
    await cmd_start(message)

async def cmd_clear(message: types.Message, user_images: dict):
    user_id = message.from_user.id
    if user_id in user_images:
        user_images[user_id] = {}
        await message.reply("✨ Все изображения очищены. Можете начать заново!")
    else:
        await message.reply("У вас нет загруженных изображений.")

async def cmd_check(message: types.Message, user_images: dict):
    user_id = message.from_user.id
    if user_id not in user_images:
        await message.reply("У вас пока нет загруженных изображений.")
        return

    status = "Статус загруженных изображений:\n"
    if 'content' in user_images[user_id]:
        status += "✅ Изображение контента загружено\n"
    else:
        status += "❌ Изображение контента не загружено\n"
        
    if 'style' in user_images[user_id]:
        status += "✅ Изображение стиля загружено\n"
    else:
        status += "❌ Изображение стиля не загружено\n"
        
    await message.reply(status)

async def set_commands(bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Помощь по использованию"),
        BotCommand(command="/style", description="Начать перенос стиля"),
        BotCommand(command="/cancel", description="Отменить текущую операцию")
    ]
    await bot.set_my_commands(commands)