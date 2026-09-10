from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    LessonListCreateAPIView,
    LessonRetrieveUpdateDestroyAPIView,
    SubscriptionCreateAPIView,
    SubscriptionDestroyAPIView
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('lessons/', LessonListCreateAPIView.as_view()),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view()),
    # Подписка
    path('courses/<int:course_id>/subscribe/', SubscriptionCreateAPIView.as_view()),
    path('courses/<int:course_id>/unsubscribe/', SubscriptionDestroyAPIView.as_view()),
]
