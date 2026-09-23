from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from materials.models import Course, Subscription


@shared_task
def send_course_update_notification(course_id):
    """
    Отправляет письмо всем подписчикам курса о его обновлении.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return f"Course {course_id} not found"

    # Берём email всех подписчиков этого курса
    subscribers = Subscription.objects.filter(course=course).select_related("user")
    recipient_list = [sub.user.email for sub in subscribers]

    if not recipient_list:
        return f"No subscribers for course '{course.title}'"

    subject = f"Обновление курса: {course.title}"
    message = (
        f"Здравствуйте!\n\n"
        f"Курс «{course.title}», на который вы подписаны, был обновлён.\n"
        f"Проверьте новые материалы на платформе.\n\n"
        f"С уважением,\nКоманда LMS"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )

    return f"Notification sent to {len(recipient_list)} subscribers for '{course.title}'"
