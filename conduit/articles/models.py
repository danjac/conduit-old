from django.conf import settings
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel


class Article(TimeStampedModel):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    body = models.TextField()

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # tags = TaggedField()

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["created", "-created"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("articles:detail", args=[self.slug])


class Comment(TimeStampedModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    body = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=["created", "-created"]),
        ]
