from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import CustomUser


class Category(models.Model):
    """Category model."""
    name = models.CharField(
        verbose_name='Category',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Category slug',
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Genre model"""
    name = models.CharField(
        verbose_name='Genre',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Genre slug',
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Title model."""
    name = models.CharField(
        verbose_name='Title',
        max_length=200,
    )
    year = models.IntegerField(
        verbose_name='Year',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Category',
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name='Description',
        max_length=255,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Genre',
        through='TitleGenre',
    )
    rating = models.FloatField(
        verbose_name='Rating',
        null=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    """Model connecting genres and titles."""

    title = models.ForeignKey(
        Title,
        verbose_name='Title',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    genre = models.ForeignKey(
        Genre,
        verbose_name='Genre',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Genre title'
        verbose_name_plural = 'Genres titles'

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    """Review model"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение'
    )
    text = models.CharField(
        max_length=500
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='author'
    )
    score = models.IntegerField(
        verbose_name='score',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={'validators': 'Score must be from 1 to 10'}
    )
    pub_date = models.DateTimeField(
        verbose_name='date published',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique_review'
            )]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text

    def update_title_rating(self):
        rating = self.title.reviews.aggregate(
            models.Avg('score')
        )['score__avg']
        self.title.rating = rating
        self.title.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_title_rating()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_title_rating()


class Comment(models.Model):
    """Comment model"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='comments'
    )
    text = models.CharField(
        'текст комментария',
        max_length=200
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='author'
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return self.text
