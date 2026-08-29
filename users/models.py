from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер пользователя — без username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Пользователь с авторизацией по email."""
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    avatar = models.ImageField(upload_to='users/', blank=True, null=True, verbose_name='Аватарка')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()  # <-- вот это главное!

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Payment(models.Model):
    """Платёж за курс или урок."""

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Наличные'
        TRANSFER = 'transfer', 'Перевод на счет'

    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, verbose_name='Пользователь',
        related_name='payments'
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')
    paid_course = models.ForeignKey(
        'materials.Course', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Оплаченный курс', related_name='payments'
    )
    paid_lesson = models.ForeignKey(
        'materials.Lesson', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Оплаченный урок', related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Сумма оплаты'
    )
    method = models.CharField(
        max_length=20, choices=PaymentMethod.choices,
        default=PaymentMethod.TRANSFER, verbose_name='Способ оплаты'
    )

    def __str__(self):
        return f'{self.user.email} — {self.amount} руб.'

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-date']
