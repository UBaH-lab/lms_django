from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def block_inactive_users():
    """
    Периодическая задача: блокирует пользователей (is_active=False),
    которые не заходили более 1 месяца (по полю last_login).
    Обновление батчем, а не по одному.
    """
    one_month_ago = timezone.now() - timedelta(days=30)

    # Выбираем пользователей: есть last_login, не заходил > 30 дней, ещё активен
    inactive_users = User.objects.filter(
        last_login__isnull=False,        # last_login заполнен
        last_login__lt=one_month_ago,    # последний вход был > месяца назад
        is_active=True,                  # ещё не заблокирован
    )

    count = inactive_users.count()

    if count == 0:
        return "No inactive users found."

    # Батч-обновление — один SQL-запрос, а не по одному
    inactive_users.update(is_active=False)

    return f"Blocked {count} inactive users (last login > 30 days)."
