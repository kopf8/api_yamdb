from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Title(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            )
        ]

    def __str__(self):
        return 'Отзыв на {self.title} от {self.author}'
