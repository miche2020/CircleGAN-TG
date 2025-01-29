import torch
import logging
from pathlib import Path

class StyleTransferModel:
    def __init__(self, model_path: str):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model(model_path)
        
    def _load_model(self, model_path: str):
        """Загрузка модели из файла"""
        try:
            if not Path(model_path).exists():
                raise FileNotFoundError(f"Файл модели не найден: {model_path}")
                
            model = torch.load(model_path, map_location=self.device)
            model.eval()
            logging.info(f"Модель успешно загружена с устройства: {self.device}")
            return model
            
        except Exception as e:
            logging.error(f"Ошибка при загрузке модели: {str(e)}")
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