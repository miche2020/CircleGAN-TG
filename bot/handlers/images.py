import io
import logging
from aiogram import types
from bot.keyboards import get_style_strength_keyboard, get_restart_keyboard
from utils.preprocessing import preprocess_image

async def handle_photo(message: types.Message, user_images: dict):
    try:
        user_id = message.from_user.id
        photo = message.photo[-1]
        
        # Получаем и скачиваем файл
        file = await message.bot.get_file(photo.file_id)
        downloaded_file = await message.bot.download_file(file.file_path)
        
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
                keyboard = get_style_strength_keyboard(user_id)
                await message.reply("✅ Изображение стиля сохранено!\nВыберите степень стилизации:", reply_markup=keyboard)
            
            else:
                keyboard = get_restart_keyboard(user_id)
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