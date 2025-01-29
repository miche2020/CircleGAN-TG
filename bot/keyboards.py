from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_style_strength_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для выбора степени стилизации"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🔅 Низкая (0.5)", callback_data=f"style_0.5_{user_id}"),
        InlineKeyboardButton("✨ Средняя (1.0)", callback_data=f"style_1.0_{user_id}"),
        InlineKeyboardButton("💫 Высокая (4.0)", callback_data=f"style_4.0_{user_id}")
    )
    return keyboard

def get_restart_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для перезапуска"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔄 Начать заново", callback_data=f"clear_{user_id}"))
    return keyboard

def get_result_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура после генерации изображения"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🔄 Начать заново", callback_data=f"clear_{user_id}"),
        InlineKeyboardButton("🎨 Другая степень", callback_data=f"retry_{user_id}")
    )
    return keyboard