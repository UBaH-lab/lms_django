import os
from celery import Celery

# Берём настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("lms_django")

# Читаем настройки с префиксом CELERY из settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Авто-обнаружение tasks.py во всех приложениях
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
