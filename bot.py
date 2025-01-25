import logging
import pickle
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from dotenv import load_dotenv
import os
from utils.preprocessing import preprocess_image, tensor_to_image
import torch
from PIL import Image

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
bot = Bot(token=os.getenv('BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Загружаем модель
with open('model.pkl', 'rb') as file:
    model = pickle.load(file)

# Добавим словарь для хранения изображений пользователей
user_images = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот с вашей моделью. Отправьте мне данные для анализа.")

@dp.message_handler()
async def process_message(message: types.Message):
    try:
        # Здесь нужно добавить предобработку входных данных в соответствии с вашей моделью
        input_data = message.text  # Преобразуйте текст в формат, который ожидает ваша модель
        
        # Получаем предсказание модели
        prediction = model.predict([input_data])  # Измените в соответствии с вашей моделью
        
        # Отправляем результат пользователю
        await message.reply(f"Результат анализа: {prediction}")
        
    except Exception as e:
        await message.reply(f"Произошла ошибка при обработке данных: {str(e)}")

@dp.message_handler(commands=['style'])
async def start_style_transfer(message: types.Message):
    await message.reply("Пожалуйста, отправьте контентное изображение")
    user_images[message.from_user.id] = {'state': 'waiting_content'}

@dp.message_handler(content_types=['photo'])
async def process_photo(message: types.Message):
    try:
        user_id = message.from_user.id
        
        if user_id not in user_images or user_images[user_id].get('state') not in ['waiting_content', 'waiting_style']:
            await message.reply("Пожалуйста, начните процесс командой /style")
            return

        # Получаем файл
        photo = message.photo[-1]
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path

        # Формируем имя временного файла
        temp_filename = f'temp_{user_id}_{user_images[user_id]["state"]}.jpg'
        
        # Скачиваем файл
        await bot.download_file(file_path, temp_filename)
        
        # Обрабатываем в зависимости от состояния
        if user_images[user_id]['state'] == 'waiting_content':
            user_images[user_id]['content'] = preprocess_image(temp_filename)
            user_images[user_id]['state'] = 'waiting_style'
            await message.reply("Отлично! Теперь отправьте стилевое изображение")
        
        elif user_images[user_id]['state'] == 'waiting_style':
            user_images[user_id]['style'] = preprocess_image(temp_filename)
            
            # Генерируем результат
            with torch.no_grad():
                output = model.generate(
                    user_images[user_id]['content'],
                    user_images[user_id]['style'],
                    1.5
                )
            
            # Сохраняем результат
            result_image = tensor_to_image(output)
            result_filename = f'result_{user_id}.jpg'
            Image.fromarray((result_image * 255).astype('uint8')).save(result_filename)
            
            # Отправляем результат
            with open(result_filename, 'rb') as photo:
                await message.reply_photo(photo)
            
            # Очищаем временные файлы и данные
            for filename in [f'temp_{user_id}_waiting_content.jpg', 
                           f'temp_{user_id}_waiting_style.jpg',
                           result_filename]:
                if os.path.exists(filename):
                    os.remove(filename)
            
            del user_images[user_id]
        
    except Exception as e:
        await message.reply(f"Произошла ошибка при обработке изображения: {str(e)}")
        if user_id in user_images:
            del user_images[user_id]

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True) 