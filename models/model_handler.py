import torch
import logging
from pathlib import Path
import sys
from .model_classes import Model, VGGEncoder, Decoder, RC, adain, calc_mean_std
import pickle

# Добавляем класс CustomUnpickler и функцию custom_load
class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "__main__":
            module = "models.model"
        return super().find_class(module, name)

def custom_load(file_path, map_location=None):
    with open(file_path, 'rb') as f:
        model = CustomUnpickler(f).load()
    if map_location is not None:
        model = model.to(map_location)
    return model

class StyleTransferModel:
    def __init__(self, model_path: str):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # Регистрируем все классы в системе
        sys.modules['__main__'].Model = Model
        sys.modules['__main__'].VGGEncoder = VGGEncoder
        sys.modules['__main__'].Decoder = Decoder
        sys.modules['__main__'].RC = RC
        sys.modules['__main__'].adain = adain
        sys.modules['__main__'].calc_mean_std = calc_mean_std
        
        self.model = self._load_model(model_path)
        
    def _load_model(self, model_path: str):
        """Загрузка модели из файла"""
        try:
            if not Path(model_path).exists():
                raise FileNotFoundError(f"Файл модели не найден: {model_path}")
            
            logging.info(f"Начинаю загрузку модели из: {model_path}")
            
            # Загружаем состояние модели
            try:
                model = torch.load(model_path, map_location=self.device)
                model.eval()
            except Exception as load_error:
                logging.error(f"Ошибка при загрузке модели: {load_error}")
                raise
            
            logging.info(f"Модель успешно загружена на устройство: {self.device}")
            return model
            
        except Exception as e:
            logging.error(f"Ошибка при загрузке модели: {str(e)}")
            logging.error(f"Тип ошибки: {type(e).__name__}")
            logging.error(f"Детали ошибки: {str(e)}")
            raise
            
    @torch.no_grad()
    def generate(self, content_image: torch.Tensor, style_image: torch.Tensor, alpha: float = 1.0) -> torch.Tensor:
        """
        Генерация стилизованного изображения
        
        Args:
            content_image: изображение контента
            style_image: изображение стиля
            alpha: степень стилизации
            
        Returns:
            torch.Tensor: стилизованное изображение
        """
        try:
            # Переносим тензоры на нужное устройство
            content_image = content_image.to(self.device)
            style_image = style_image.to(self.device)
            
            # Генерируем изображение
            output = self.model.generate(content_image, style_image, alpha=alpha)
            
            return output.cpu()  # Возвращаем результат на CPU
            
        except Exception as e:
            logging.error(f"Ошибка при генерации изображения: {str(e)}")
            raise 