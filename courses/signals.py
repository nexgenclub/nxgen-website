from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Course, Section, Rating, CourseIssue, CourseReport

@receiver(post_save, sender=Course)
def ensure_unique_course_slug(sender, instance, created, **kwargs):
    """Ensure course slugs are unique by appending a number if needed"""
    if created:
        original_slug = instance.slug
        counter = 1
        
        # Check if the slug already exists (shouldn't happen due to unique constraint, but just to be safe)
        while Course.objects.filter(slug=instance.slug).exclude(id=instance.id).exists():
            instance.slug = f"{original_slug}-{counter}"
            counter += 1
            
        if instance.slug != original_slug:
            # Save the instance with the updated slug, but don't trigger the signal again
            instance.save(update_fields=['slug'])

@receiver(post_save, sender=Rating)
def update_course_on_rating(sender, instance, created, **kwargs):
    """Recalculate average rating when a rating is added or modified"""
    # The average rating is calculated on demand in the model method, so nothing to do here
    # But we could add other processing if needed, like notifications

@receiver(post_save, sender=CourseIssue)
def send_issue_notification(sender, instance, created, **kwargs):
    """Send notification to course author when a new issue is created"""
    # This would integrate with a notification system
    # For now, it's a placeholder for future functionality
    if created:
        # Notification logic would go here
        pass

@receiver(post_save, sender=CourseReport)
def handle_course_moderation(sender, instance, **kwargs):
    """Handle automatic actions when a report is actioned"""
    # If a report is actioned, we may want to take actions on the course
    if instance.status == 'actioned' and instance.course.status != 'moderated':
        instance.course.status = 'moderated'
        instance.course.save(update_fields=['status'])
