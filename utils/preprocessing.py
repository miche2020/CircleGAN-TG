import torch
from torchvision import  transforms
from PIL import Image
from typing import Union
import numpy as np
import io
import logging

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

IMAGE_SIZE  = 512
# Определяем преобразования как в обучении
transform = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.CenterCrop(256),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def preprocess_image(image_bytes: io.BytesIO) -> torch.Tensor:
    """
    Преобразует изображение из байтов в тензор для модели
    
    Args:
        image_bytes: входное изображение в виде байтов
    Returns:
        tensor: предобработанный тензор
    """
    try:
        # Открываем изображение из байтов
        image = Image.open(image_bytes)
        
        # Проверяем размеры
        if image.width < 32 or image.height < 32:
            raise ValueError("Изображение слишком маленькое (минимум 32x32)")
        if image.width > 2048 or image.height > 2048:
            raise ValueError("Изображение слишком большое (максимум 2048x2048)")
        
        # Преобразуем в RGB если нужно
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Изменяем размер
        image = image.resize((256, 256), Image.LANCZOS)
        
        # Преобразуем в numpy array
        img_array = np.array(image)
        
        # Нормализуем значения
        img_array = img_array.astype(np.float32) / 255.0
        
        # Преобразуем в тензор и добавляем batch dimension
        tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0)
        
        return tensor
        
    except Exception as e:
        logging.error(f"Ошибка в preprocess_image: {str(e)}")
        raise


def denorm(tensor, device):
    std = torch.Tensor([0.229, 0.224, 0.225]).reshape(-1, 1, 1).to(device)
    mean = torch.Tensor([0.485, 0.456, 0.406]).reshape(-1, 1, 1).to(device)
    res = torch.clamp(tensor * std + mean, 0, 1)
    return res

def tensor_to_image(tensor: torch.Tensor) -> np.ndarray:
    """
    Преобразование тензора в numpy array для отображения
    
    Args:
        tensor: входной тензор
    Returns:
        image: изображение в формате numpy array
    """
    # Отключаем градиенты
    with torch.no_grad():
        # Денормализуем и переводим в CPU
        image = denorm(tensor.detach(), device).squeeze(0).permute(1, 2, 0).cpu()
        # Конвертируем в numpy и обрезаем значения
        return np.clip(image.numpy(), 0, 1) 