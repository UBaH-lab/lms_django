# LMS Django

Платформа для онлайн-обучения (LMS) на Django + DRF.

## Возможности

- 👤 Кастомная модель пользователя (авторизация по email)
- 📚 Курсы и уроки
- 🔗 CRUD через ViewSet и Generic-классы

## Технологии

- Python 3.13
- Django 6.1
- Django REST Framework 3.18
- SQLite

## Установка

```bash
git clone https://github.com/UBaH-lab/lms_django.git
cd lms_django
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Эндпоинты
Метод	URL	Описание
GET/POST	/api/courses/	Список курсов / создание
GET/PUT/DELETE	/api/courses/{id}/	Один курс
GET/POST	/api/lessons/	Список уроков / создание
GET/PUT/DELETE	/api/lessons/{id}/	Один урок
GET/POST	/api/users/	Список пользователей / создание
GET/PUT/DELETE	/api/users/{id}/	Один пользователь
---

### 2. Создай `requirements.txt` (заодно пригодится)

```bash
pip freeze > requirements.txt
```