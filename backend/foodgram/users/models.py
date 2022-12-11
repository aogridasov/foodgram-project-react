from django.contrib.auth.models import AbstractUser
from django.db import models


ROLES = (
    ('admin', 'Администратор'),
    ('user', 'Пользователь')
)


class User(AbstractUser):
    """Модель пользователя"""
    role = models.CharField(
        max_length=10,
        choices=ROLES,
        default='user'
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True
    )
    first_name = models.CharField(
        max_length=10,
        blank=False,
    )
    last_name = models.CharField(
        max_length=10,
        blank=False,
    )

    REQUIRED_FIELDS = ['role', 'email', 'first_name', 'last_name', ]


class Subscribe(models.Model):
    """Модель, реализующая подписку на пользователя"""
    user = models.ForeignKey(
        User,
        related_name='follows',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='follower',
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
