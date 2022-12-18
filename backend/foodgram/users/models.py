from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""
    username = models.CharField(
        max_length=settings.USER_MODELS_FIELD_LENGTH,
        unique=True,
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        max_length=settings.USER_MODELS_EMAIL_FIELD_LENGTH,
    )
    first_name = models.CharField(
        max_length=settings.USER_MODELS_FIELD_LENGTH,
    )
    last_name = models.CharField(
        max_length=settings.USER_MODELS_FIELD_LENGTH,
    )

    REQUIRED_FIELDS = [
        'username', 'first_name', 'last_name',
    ]
    USERNAME_FIELD = 'email'


class Subscribe(models.Model):
    """Модель, реализующая подписку на пользователя"""
    user = models.ForeignKey(
        User,
        related_name='subscribed_to',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='subscribed',
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f'{self.user} is subcribed to {self.author}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='no_self_subscribe'
            ),

            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribing'
            )
        ]
