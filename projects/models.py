from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    github_link = models.URLField(max_length=500, blank=False, null=False)
    tech_stack = models.CharField(max_length=255, help_text="Comma-separated list of technologies")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_seeking_collaborators = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
