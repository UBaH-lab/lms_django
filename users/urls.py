from django.urls import path
from .views import (
    UserListCreateAPIView,
    UserRetrieveAPIView,
    UserUpdateAPIView,
    PaymentListAPIView,
    UserCreateAPIView,
    PaymentCreateAPIView,
    PaymentStatusAPIView,
)

urlpatterns = [
    path('users/', UserListCreateAPIView.as_view()),
    path('users/<int:pk>/', UserRetrieveAPIView.as_view()),
    path('users/<int:pk>/update/', UserUpdateAPIView.as_view()),
    path('users/register/', UserCreateAPIView.as_view()),
    path('payments/', PaymentListAPIView.as_view()),
    path('payments/create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('payments/<str:session_id>/status/', PaymentStatusAPIView.as_view(), name='payment-status'),
]
