from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, Payment
from .serializers import UserSerializer, UserPublicSerializer, PaymentSerializer
from materials.services import (
    create_stripe_product, create_stripe_price, create_stripe_session
)
from rest_framework.response import Response
from rest_framework import status as http_status


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей с фильтрацией и сортировкой."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'method']
    ordering_fields = ['date']
    permission_classes = [IsAuthenticated]


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр профиля — свой полностью, чужой без sensitive."""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.id == self.get_object().id:
            return UserSerializer
        return UserPublicSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    """Редактирование только своего профиля."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class PaymentCreateAPIView(generics.CreateAPIView):
    """Создание платежа через Stripe."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        amount = request.data.get('amount')

        if not course_id or not amount:
            return Response(
                {'error': 'Нужны course_id и amount'},
                status=http_status.HTTP_400_BAD_REQUEST
            )

        from materials.models import Course
        course = Course.objects.get(id=course_id)

        product_id = create_stripe_product(
            name=course.title,
            description=course.description or ''
        )

        price_id = create_stripe_price(amount=amount, product_id=product_id)

        session = create_stripe_session(price_id)

        payment = Payment.objects.create(
            user=request.user,
            paid_course=course,
            amount=amount,
            method='stripe',
            stripe_product_id=product_id,
            stripe_price_id=price_id,
            stripe_session_id=session.id,
            payment_url=session.url,
        )

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=http_status.HTTP_201_CREATED)


class PaymentStatusAPIView(generics.RetrieveAPIView):
    """Проверка статуса платежа через Stripe."""
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        session_id = kwargs.get('session_id')
        from materials.services import retrieve_stripe_session
        session = retrieve_stripe_session(session_id)
        return Response({
            'status': session.payment_status,
            'is_paid': session.payment_status == 'paid'
        })
