from django.urls import path
from .views import UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('users/', UserListCreateAPIView.as_view()),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view()),
]
