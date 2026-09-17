from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import YouTubeValidator


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока."""

    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [YouTubeValidator(field='video_link')]


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
