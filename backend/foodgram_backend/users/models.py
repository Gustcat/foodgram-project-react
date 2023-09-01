from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Subscription(models.Model):
    subscriber = models.ForeignKey(User,
                                   on_delete=models.CASCADE,
                                   related_name='subscriber',
                                   verbose_name='Подписчик')
    subscribing = models.ForeignKey(User,
                                    on_delete=models.CASCADE,
                                    related_name='subscribing',
                                    verbose_name='Автор')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['subscriber', 'subscribing'],
            name='unique_subscriber_subscribing')]
