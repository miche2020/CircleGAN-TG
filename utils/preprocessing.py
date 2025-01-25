import torch
from torchvision import  transforms
from PIL import Image
from typing import Union
import numpy as np

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

IMAGE_SIZE  = 512
# Определяем преобразования как в обучении
transform = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.CenterCrop(256),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def preprocess_image(image_path: str) -> torch.Tensor:
    """
    Препроцессинг изображения перед подачей в модель
    
    Args:
        image_path: путь к изображению
    Returns:
        preprocessed_image: обработанное изображение в формате torch.Tensor
    """
    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(device)
    return image_tensor


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
    image = denorm(tensor, device).squeeze(0).permute(1, 2, 0).cpu().numpy()
    return np.clip(image, 0, 1) 