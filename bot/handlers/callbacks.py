import logging
import torch
from aiogram import types
from PIL import Image
import io
import numpy as np
from bot.keyboards import get_style_strength_keyboard, get_result_keyboard
from utils.preprocessing import tensor_to_image

async def process_style_transfer(callback_query: types.CallbackQuery, user_images: dict, model):
    try:
        parts = callback_query.data.split('_')
        alpha = float(parts[1])
        user_id = int(parts[2])
        
        if user_id not in user_images or 'content' not in user_images[user_id] or 'style' not in user_images[user_id]:
            await callback_query.message.answer("❌ Ошибка: изображения не найдены")
            return
            
        await callback_query.message.answer("🎨 Начинаю обработку...")
        
        with torch.no_grad():
            output = model.generate(
                user_images[user_id]['content'],
                user_images[user_id]['style'],
                alpha=alpha
            )
            
            output_array = tensor_to_image(output)
            output_image = Image.fromarray((output_array * 255).astype(np.uint8))
            
            img_bio = io.BytesIO()
            output_image.save(img_bio, 'JPEG')
            img_bio.seek(0)
            
            keyboard = get_result_keyboard(user_id)
            
            await callback_query.message.answer_photo(
                photo=img_bio,
                caption=f"✨ Готово! Степень стилизации: {'низкая' if alpha == 0.5 else 'средняя' if alpha == 1.0 else 'высокая'}",
                reply_markup=keyboard
            )
            
    except Exception as e:
        logging.error(f"Ошибка при обработке: {str(e)}")
        await callback_query.message.answer(f"❌ Ошибка при обработке: {str(e)}")

async def clear_images_callback(callback_query: types.CallbackQuery, user_images: dict):
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

async def retry_style_transfer(callback_query: types.CallbackQuery):
    try:
        _, user_id = callback_query.data.split('_')
        user_id = int(user_id)
        
        keyboard = get_style_strength_keyboard(user_id)
        await callback_query.message.answer("Выберите новую степень стилизации:", reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        await callback_query.message.answer("❌ Произошла ошибка")
