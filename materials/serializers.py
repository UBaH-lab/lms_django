from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Course, Lesson, Subscription
from .validators import YouTubeValidator


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока."""

    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [YouTubeValidator(field='video_link')]

    def validate(self, data):
        """Проверка: между уроками одного курса должно быть не менее 4 часов."""
        course = data.get('course') or (self.instance.course if self.instance else None)
        if not course:
            return data

        # Ищем последний урок на этом курсе
        last_lesson = (
            Lesson.objects.filter(course=course)
            .exclude(pk=self.instance.pk if self.instance else None)
            .order_by('-created_at')
            .first()
        )

        if last_lesson:
            time_diff = timezone.now() - last_lesson.created_at
            if time_diff < timedelta(hours=4):
                raise serializers.ValidationError(
                    f"Нельзя создать урок раньше, чем через 4 часа после последнего. "
                    f"Последний урок создан: {last_lesson.created_at.strftime('%d.%m.%Y %H:%M')}"
                )

        return data


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса с уроками, количеством и признаком подписки."""

    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Признак подписки текущего пользователя на курс."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False

    class Meta:
        model = Course
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
