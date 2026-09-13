from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, Payment

User = get_user_model()


class UserEndpointsTestCase(TestCase):
    """Тесты всех пользовательских эндпоинтов."""

    def setUp(self):
        """Подготовка данных."""
        self.client = APIClient()

        # Пользователь 1
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123',
            first_name='Иван',
            last_name='Иванов',
            city='Казань'
        )

        # Пользователь 2
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123',
            first_name='Пётр',
            last_name='Петров',
            city='Москва'
        )

    # === РЕГИСТРАЦИЯ ===

    def test_register(self):
        """Регистрация нового пользователя."""
        data = {
            'email': 'new@test.com',
            'password': 'newpass123'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='new@test.com').exists())

    # === JWT ТОКЕНЫ ===

    def test_jwt_token(self):
        """Получение JWT токена."""
        data = {
            'email': 'user1@test.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/token/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_jwt_token_wrong_password(self):
        """JWT с неверным паролем — ошибка."""
        data = {
            'email': 'user1@test.com',
            'password': 'wrongpass'
        }
        response = self.client.post('/api/token/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_refresh(self):
        """Обновление JWT токена."""
        # Получаем токен
        data = {
            'email': 'user1@test.com',
            'password': 'testpass123'
        }
        token_response = self.client.post('/api/token/', data)
        refresh_token = token_response.data['refresh']

        # Обновляем
        response = self.client.post('/api/token/refresh/', {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    # === СПИСОК ПОЛЬЗОВАТЕЛЕЙ ===

    def test_user_list_unauthorized(self):
        """Список пользователей без авторизации — 401."""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_list_authorized(self):
        """Список пользователей с авторизацией — 200."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # === ПРОФИЛЬ ===

    def test_profile_own(self):
        """Просмотр своего профиля — полный."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/users/{self.user1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('last_name', response.data)
        self.assertIn('payments', response.data)

    def test_profile_other(self):
        """Просмотр чужого профиля — без last_name и payments."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/users/{self.user2.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('last_name', response.data)
        self.assertNotIn('payments', response.data)

    # === РЕДАКТИРОВАНИЕ ПРОФИЛЯ ===

    def test_profile_update_own(self):
        """Редактирование своего профиля — можно."""
        self.client.force_authenticate(user=self.user1)
        data = {'city': 'Елабуга'}
        response = self.client.patch(f'/api/users/{self.user1.id}/update/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.city, 'Елабуга')

    def test_profile_update_other(self):
        """Редактирование чужого профиля — нельзя."""
        self.client.force_authenticate(user=self.user1)
        data = {'city': 'Хакасия'}
        response = self.client.patch(f'/api/users/{self.user2.id}/update/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # === ПЛАТЕЖИ ===

    def test_payments_unauthorized(self):
        """Платежи без авторизации — 401."""
        response = self.client.get('/api/payments/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payments_authorized(self):
        """Платежи с авторизацией — 200."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/payments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
