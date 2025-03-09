from django.db import models

class LeadershipTeam(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='leadership/')
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    whatsapp = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Testimonial(models.Model):
    content = models.TextField()
    author_name = models.CharField(max_length=100)
    author_position = models.CharField(max_length=100)
    author_image = models.ImageField(upload_to='testimonials/')

    def __str__(self):
        return self.author_name
