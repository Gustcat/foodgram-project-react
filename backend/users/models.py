from rest_framework.exceptions import ValidationError
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

    def validate_unique(self, exclude=None):
        if self.subscriber == self.subscribing:
            raise ValidationError("Подписка на себя невозможна")
        if Subscription.objects.filter(
                subscriber=self.subscriber,
                subscribing=self.subscribing):
            raise ValidationError("Подписка уже есть")
        super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)
