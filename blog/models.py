from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to="posts/images/", null=True, blank=True)
    background_image = models.ImageField(
        upload_to="posts/backgrounds/", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Create your models here.
