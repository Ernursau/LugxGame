# apps.py
from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'  # замените на имя вашего приложения

    def ready(self):
        import main.signals  # или ваше_приложение.signals
