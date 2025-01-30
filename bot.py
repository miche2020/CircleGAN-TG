import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from dotenv import load_dotenv
import os
from utils.preprocessing import preprocess_image, tensor_to_image
import torch
from PIL import Image
import io
import numpy as np
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models.model_handler import StyleTransferModel
from config import MODEL_PATH

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
bot = Bot(token=os.getenv('BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализируем обработчик модели
model_handler = StyleTransferModel(MODEL_PATH)
model = model_handler.model

# Словарь для хранения изображений пользователей
user_images = {}

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
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

@dp.message_handler(commands=['clear'])
async def clear_images(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_images:
        user_images[user_id] = {}
        await message.reply("✨ Все изображения очищены. Можете начать заново!")
    else:
        await message.reply("У вас нет загруженных изображений.")

@dp.message_handler(commands=['check'])
async def check_images(message: types.Message):
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

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    try:
        user_id = message.from_user.id
        photo = message.photo[-1]
        
        # Получаем и скачиваем файл
        file = await bot.get_file(photo.file_id)
        downloaded_file = await bot.download_file(file.file_path)
        
        # Создаем BytesIO объект из скачанных данных
        image_bytes = io.BytesIO(downloaded_file.read())
        
        try:
            # Преобразуем изображение
            processed_image = preprocess_image(image_bytes)
            
            # Инициализируем словарь пользователя
            if user_id not in user_images:
                user_images[user_id] = {}
            
            # Определяем тип изображения
            if 'content' not in user_images[user_id]:
                user_images[user_id]['content'] = processed_image
                await message.reply("✅ Изображение контента сохранено!\nТеперь отправьте изображение стиля.")
            
            elif 'style' not in user_images[user_id]:
                user_images[user_id]['style'] = processed_image
                keyboard = InlineKeyboardMarkup(row_width=1)
                keyboard.add(
                    InlineKeyboardButton("🔅 Низкая (0.5)", callback_data=f"style_0.5_{user_id}"),
                    InlineKeyboardButton("✨ Средняя (1.0)", callback_data=f"style_1.0_{user_id}"),
                    InlineKeyboardButton("💫 Высокая (4.0)", callback_data=f"style_4.0_{user_id}")
                )
                await message.reply("✅ Изображение стиля сохранено!\nВыберите степень стилизации:", reply_markup=keyboard)
            
            else:
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("🔄 Начать заново", callback_data=f"clear_{user_id}"))
                await message.reply(
                    "У вас уже загружены оба изображения!\n"
                    "Нажмите кнопку ниже, чтобы начать заново:",
                    reply_markup=keyboard
                )
                
        except Exception as img_error:
            logging.error(f"Ошибка обработки изображения: {str(img_error)}")
            await message.reply("❌ Не удалось обработать изображение. Попробуйте другое изображение.")
            return
            
    except Exception as e:
        logging.error(f"Ошибка при обработке фото: {str(e)}")
        await message.reply("❌ Произошла ошибка при обработке изображения.")

@dp.callback_query_handler(lambda c: c.data.startswith('style_'))
async def process_style_transfer(callback_query: types.CallbackQuery):
    try:
        parts = callback_query.data.split('_')
        alpha = float(parts[1])
        user_id = int(parts[2])
        
        if user_id not in user_images or 'content' not in user_images[user_id] or 'style' not in user_images[user_id]:
            await callback_query.message.answer("❌ Ошибка: изображения не найдены")
            return
            
        await callback_query.message.answer("🎨 Начинаю обработку...")
        
        # Генерируем изображение
        with torch.no_grad():
            output = model.generate(
                user_images[user_id]['content'],
                user_images[user_id]['style'],
                alpha=alpha
            )
            
            # Преобразуем в изображение
            output_array = tensor_to_image(output)
            output_image = Image.fromarray((output_array * 255).astype(np.uint8))
            
            # Сохраняем в буфер
            img_bio = io.BytesIO()
            output_image.save(img_bio, 'JPEG')
            img_bio.seek(0)
            
            # Создаем клавиатуру
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                InlineKeyboardButton("🔄 Начать заново", callback_data=f"clear_{user_id}"),
                InlineKeyboardButton("🎨 Другая степень", callback_data=f"retry_{user_id}")
            )
            
            # Отправляем результат
            await callback_query.message.answer_photo(
                photo=img_bio,
                caption=f"✨ Готово! Степень стилизации: {'низкая' if alpha == 0.5 else 'средняя' if alpha == 1.0 else 'высокая'}",
                reply_markup=keyboard
            )
            
    except Exception as e:
        logging.error(f"Ошибка при обработке: {str(e)}")
        await callback_query.message.answer(f"❌ Ошибка при обработке: {str(e)}")

@dp.callback_query_handler(lambda c: c.data.startswith('clear_'))
async def clear_images_callback(callback_query: types.CallbackQuery):
    try:
        _, user_id = callback_query.data.split('_')
        user_id = int(user_id)
        
        if user_id in user_images:
            user_images[user_id] = {}
            await callback_query.message.answer(
                "✨ Все изображения очищены!\n"
                "1. Отправьте изображение контента\n"
                "2. Затем отправьте изображение стиля"
            )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Ошибка при очистке: {str(e)}")
        await callback_query.message.answer("❌ Произошла ошибка при очистке изображений.")

@dp.callback_query_handler(lambda c: c.data.startswith('retry_'))
async def retry_style_transfer(callback_query: types.CallbackQuery):
    try:
        _, user_id = callback_query.data.split('_')
        user_id = int(user_id)
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("🔅 Низкая (0.5)", callback_data=f"style_0.5_{user_id}"),
            InlineKeyboardButton("✨ Средняя (1.0)", callback_data=f"style_1.0_{user_id}"),
            InlineKeyboardButton("💫 Высокая (4.0)", callback_data=f"style_4.0_{user_id}")
        )
        
        await callback_query.message.answer("Выберите новую степень стилизации:", reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        await callback_query.message.answer("❌ Произошла ошибка")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True) 