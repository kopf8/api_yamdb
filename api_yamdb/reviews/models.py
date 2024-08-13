from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_username, validate_year

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]


class CustomUser(AbstractUser):
    """Custom User model"""
    username = models.CharField(
        verbose_name='Username',
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        verbose_name='User Role',
        max_length=16,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    bio = models.TextField(
        verbose_name='User bio',
        blank=True,
    )
    first_name = models.CharField(
        verbose_name='First name',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Last name',
        max_length=150,
        blank=True
    )
    confirmation_code = models.CharField(
        verbose_name='Confirmation code',
        max_length=255,
        null=True,
        blank=False,
    )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


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
        validators=(validate_year, )
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
