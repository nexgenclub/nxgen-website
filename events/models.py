# models.py
import logging
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.text import slugify

logger = logging.getLogger(__name__)

class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Event Categories"
        ordering = ['name']

class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=250, blank=True)
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_deadline = models.DateTimeField(blank=True, null=True)
    
    location = models.CharField(max_length=200)
    is_virtual = models.BooleanField(default=False)
    virtual_link = models.URLField(blank=True, null=True)
    
    image = models.ImageField(upload_to='events/%Y/%m/%d/', blank=True)
    capacity = models.PositiveIntegerField(blank=True, null=True)
    
    categories = models.ManyToManyField(EventCategory, related_name='events')
    organizers = models.ManyToManyField(User, related_name='organized_events')
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['-start_date']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('events:event_detail', args=[self.slug])
    
    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    @property
    def is_past(self):
        return self.end_date < timezone.now()
    
    @property
    def registration_open(self):
        if not self.registration_deadline:
            return self.is_upcoming
        return timezone.now() <= self.registration_deadline

    def get_similar_events(self):
        """
        Get similar events based on categories.
        Returns up to 3 upcoming or ongoing events from the same categories.
        """
        from django.utils import timezone
        
        # Get the event's categories
        categories = self.categories.all()
        
        # Get upcoming or ongoing events in the same categories, excluding this event
        now = timezone.now()
        similar_events = Event.objects.filter(
            categories__in=categories,
            end_date__gte=now,
            status='published'
        ).exclude(id=self.id).distinct()
        
        # Return up to 3 events
        return similar_events[:3]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            if Event.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}"
        super().save(*args, **kwargs)
        logger.debug(f"Saved event: {self}")

    
    # Add these properties to your Event model in models.py

    @property
    def registration_percentage(self):
        """Calculate the percentage of capacity filled by registrations."""
        if not self.capacity:
            return 0
        return min(100, (self.registrations.count() / self.capacity) * 100)

    @property
    def spots_left(self):
        """Calculate the number of spots left."""
        if not self.capacity:
            return None  # Unlimited capacity
        return max(0, self.capacity - self.registrations.count())

    @property
    def is_full(self):
        """Check if the event has reached capacity."""
        if not self.capacity:
            return False  # Unlimited capacity
        return self.registrations.count() >= self.capacity
    
    def register_user(self, user):
        """Register a user for this event if possible."""
        if not self.registration_open:
            return False, "Registration is closed for this event."
        
        if self.is_full:
            return False, "This event has reached its capacity."
        
        if Registration.objects.filter(event=self, attendee=user).exists():
            return False, "You are already registered for this event."
        
        Registration.objects.create(
            event=self,
            attendee=user,
            status='confirmed'
        )
        return True, "You've successfully registered for this event!"

    def unregister_user(self, user):
        """Unregister a user from this event."""
        try:
            registration = Registration.objects.get(event=self, attendee=user)
            registration.delete()
            return True, "Your registration has been canceled."
        except Registration.DoesNotExist:
            return False, "You are not registered for this event."
    
    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Handle slug uniqueness
        original_slug = self.slug
        counter = 1
        
        # Check if slug exists, and if so, append a suffix
        while Event.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Call the original save method
        super().save(*args, **kwargs)
        logger.debug(f"Saved event: {self}")

# models.py - Registration model
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Registration(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('attended', 'Attended'),
        ('waitlisted', 'Waitlisted'),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    attendee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Additional fields for enhanced registration
    notes = models.TextField(blank=True, help_text="Additional notes or requirements")
    check_in_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('event', 'attendee')
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['event', 'status']),  # For efficient filtering by status
            models.Index(fields=['attendee']),         # For user's registrations lookup
        ]
    
    def __str__(self):
        return f"{self.attendee.username} - {self.event.title}"
    
    def mark_as_attended(self):
        """Mark this registration as attended and record check-in time"""
        self.status = 'attended'
        self.check_in_time = timezone.now()
        self.save()
        logger.info(f"Marked registration {self.id} as attended at {self.check_in_time}")
        return True
    
    def cancel(self):
        """Cancel this registration"""
        if self.event.start_date <= timezone.now():
            return False, "Cannot cancel registration for an event that has already started"
        
        self.status = 'canceled'
        self.save()
        logger.info(f"Canceled registration {self.id}")
        return True, "Registration canceled successfully"
    
    @property
    def is_active(self):
        """Check if registration is active (confirmed or pending)"""
        return self.status in ('confirmed', 'pending')
    
    @property
    def can_cancel(self):
        """Check if registration can be canceled"""
        if self.status == 'canceled':
            return False
        if self.event.start_date <= timezone.now():
            return False
        return True