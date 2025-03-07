from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default="fas fa-comments")  
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forums:category_detail', kwargs={'slug': self.slug})
    
    def get_topic_count(self):
        return Topic.objects.filter(category=self).count()
    
    def get_post_count(self):
        return Post.objects.filter(topic__category=self).count()
    
    def get_latest_post(self):
        return Post.objects.filter(topic__category=self).order_by('-created_at').first()


class Topic(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='topics')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    pinned = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-pinned', '-updated_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
            counter = 1
            original_slug = self.slug
            while Topic.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forums:topic_detail', kwargs={'category_slug': self.category.slug, 'slug': self.slug})
    
    def get_post_count(self):
        return self.posts.count()
    
    def get_view_count(self):
        return self.views.count()
    
    def get_last_post(self):
        return self.posts.order_by('-created_at').first()


class Post(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField()
    content_html = models.TextField(blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Post by {self.author.username} on {self.topic.title}"
    
    def save(self, *args, **kwargs):
        
        import markdown
        self.content_html = markdown.markdown(
            self.content,
            extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables', 'markdown.extensions.nl2br']
        )
        
        
        if self.pk and (timezone.now() - self.created_at).seconds > 60:
            self.edited = True
            
        super().save(*args, **kwargs)
        
        
        self.topic.updated_at = timezone.now()
        self.topic.save(update_fields=['updated_at'])


class TopicView(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['topic', 'user'], ['topic', 'ip_address']]
