from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=255)
    image = models.URLField(null=True, blank=True)
    background_image = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Section(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="sections")
    description = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    section_image = models.URLField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Section {self.order} of {self.post.title}"

    class Meta:
        ordering = ["order"]
