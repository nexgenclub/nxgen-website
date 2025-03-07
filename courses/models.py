from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('courses:category_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
        ('moderated', 'Under Moderation'),
    )
    
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    description = models.TextField()
    content = models.TextField()  # This will store the main course content in markdown
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    level = models.CharField(max_length=12, choices=LEVEL_CHOICES, default='beginner')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    prerequisites = models.TextField(blank=True)
    estimated_duration = models.PositiveIntegerField(help_text="Estimated duration in minutes", null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('courses:course_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # If course is being published for the first time
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)

    def get_average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(rating.score for rating in ratings) / len(ratings)
        return 0


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Rating(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['course', 'user']  # A user can rate a course only once
    
    def __str__(self):
        return f"{self.user.username}: {self.score} for {self.course.title}"


class CourseIssue(models.Model):
    ISSUE_STATUS = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    ISSUE_TYPE = (
        ('bug', 'Bug/Error'),
        ('enhancement', 'Enhancement'),
        ('question', 'Question'),
        ('content', 'Content Issue'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='issues')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_issues')
    title = models.CharField(max_length=200)
    description = models.TextField()
    issue_type = models.CharField(max_length=15, choices=ISSUE_TYPE)
    status = models.CharField(max_length=15, choices=ISSUE_STATUS, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class IssueComment(models.Model):
    issue = models.ForeignKey(CourseIssue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.issue.title}"


class CourseEnrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrolled_courses')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['course', 'user']
    
    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class CourseReport(models.Model):
    REPORT_REASONS = (
        ('inappropriate', 'Inappropriate Content'),
        ('copyright', 'Copyright Violation'),
        ('spam', 'Spam or Misleading'),
        ('offensive', 'Offensive or Harmful'),
        ('other', 'Other'),
    )
    
    REPORT_STATUS = (
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('actioned', 'Action Taken'),
        ('dismissed', 'Dismissed'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    details = models.TextField()
    status = models.CharField(max_length=10, choices=REPORT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='reviewed_reports'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report on {self.course.title} - {self.get_reason_display()}"
