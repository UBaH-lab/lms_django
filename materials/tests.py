from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from .models import Course, Lesson, Subscription

User = get_user_model()


class MaterialsTestCase(TestCase):
    """Тесты CRUD уроков и подписки."""

    def setUp(self):
        """Подготовка данных для тестов."""
        self.client = APIClient()

        # Пользователь
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )

        # Модератор
        self.moderator = User.objects.create_user(
            email='mod@test.com',
            password='modpass123'
        )
        mod_group = Group.objects.create(name='moderators')
        self.moderator.groups.add(mod_group)

        # Курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Description',
            owner=self.user
        )

        # Урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Description',
            course=self.course,
            owner=self.user,
            video_link='https://youtube.com/watch?v=123'
        )

    def test_lesson_create(self):
        """Создание урока — только владелец (не модератор)."""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Lesson',
            'description': 'New',
            'course': self.course.id,
            'video_link': 'https://youtube.com/watch?v=456'
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_create_moderator_forbidden(self):
        """Модератор не может создавать уроки."""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'title': 'New Lesson',
            'description': 'New',
            'course': self.course.id,
            'video_link': 'https://youtube.com/watch?v=456'
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_create_bad_link(self):
        """Ссылка не на YouTube — ошибка валидации."""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Lesson',
            'description': 'New',
            'course': self.course.id,
            'video_link': 'https://vimeo.com/123'
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_list(self):
        """Список уроков — только свои."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_lesson_update(self):
        """Редактирование урока — владелец."""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Lesson'}
        response = self.client.patch(f'/api/lessons/{self.lesson.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Lesson')

    def test_lesson_delete(self):
        """Удаление урока — владелец."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lesson_delete_moderator_forbidden(self):
        """Модератор не может удалять."""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_subscription_create(self):
        """Подписка на курс."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/courses/{self.course.id}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user,
                course=self.course
            ).exists()
        )

    def test_subscription_destroy(self):
        """Отписка от курса."""
        # Сначала подписываемся
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/courses/{self.course.id}/unsubscribe/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Subscription.objects.filter(
                user=self.user,
                course=self.course
            ).exists()
        )
