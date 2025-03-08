# views.py - Fixed version

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponse
import logging
from icalendar import Calendar, Event as ICalEvent
import vobject
import icalendar

logger = logging.getLogger(__name__)

from .models import Event, EventCategory, Registration
from .forms import EventForm, RegistrationForm

class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 9
    
    def get_queryset(self):
        # Log total events for debugging
        logger.debug(f"Total events in database: {Event.objects.count()}")
        
        # Start with all events and prefetch related fields for performance
        base_queryset = Event.objects.prefetch_related(
            'categories',
            Prefetch('registrations', queryset=Registration.objects.filter(status='confirmed'), to_attr='confirmed_registrations')
        )
        
        logger.debug(f"All events count: {base_queryset.count()}")
        
        # Filter for published events or drafts if the user is an organizer or staff
        if self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.organized_events.exists()):
            queryset = base_queryset.filter(
                Q(status='published') | Q(status='draft', organizers=self.request.user)
            )
        else:
            queryset = base_queryset.filter(status='published')
        
        logger.debug(f"Published events count: {queryset.count()}")
        
        # Filter by event type (upcoming, ongoing, past)
        event_type = self.request.GET.get('type', 'upcoming')
        now = timezone.now()
        
        # Save the unfiltered published queryset for debugging
        events_before_date_filter = queryset.count()
        
        if event_type == 'upcoming':
            queryset = queryset.filter(start_date__gt=now)
        elif event_type == 'ongoing':
            queryset = queryset.filter(start_date__lte=now, end_date__gte=now)
        elif event_type == 'past':
            queryset = queryset.filter(end_date__lt=now)
        
        # Debug date filtering
        logger.debug(f"Events after type filtering ({event_type}): {queryset.count()} (from {events_before_date_filter})")
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        
        # Order by start date (upcoming first, then ongoing, then past)
        if event_type == 'past':
            # For past events, show the most recent ones first
            return queryset.order_by('-end_date')
        else:
            # For upcoming and ongoing events, show the soonest ones first
            return queryset.order_by('start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = EventCategory.objects.all()
        
        # Add filter parameters to context for maintaining state in templates
        context['current_type'] = self.request.GET.get('type', 'upcoming')
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Count events by type for display in filter buttons
        now = timezone.now()
        context['upcoming_count'] = Event.objects.filter(status='published', start_date__gt=now).count()
        context['ongoing_count'] = Event.objects.filter(status='published', start_date__lte=now, end_date__gte=now).count()
        context['past_count'] = Event.objects.filter(status='published', end_date__lt=now).count()
        
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    
    def get_object(self):
        logger.debug(f"Looking for event with slug: {self.kwargs['slug']}")
        
        # Query to get the event with needed prefetches for performance
        queryset = Event.objects.prefetch_related(
            'categories',
            'organizers',
            Prefetch('registrations', queryset=Registration.objects.filter(status='confirmed').select_related('attendee'))
        )
        
        try:
            if self.request.user.is_authenticated:
                # If user is logged in, they might be an organizer
                event = get_object_or_404(
                    queryset,
                    Q(status='published') | Q(organizers=self.request.user),
                    slug=self.kwargs['slug']
                )
            else:
                # Anonymous users can only see published events
                event = get_object_or_404(
                    queryset,
                    status='published',
                    slug=self.kwargs['slug']
                )
            
            logger.debug(f"Found event: {event}")
            return event
        except Http404:
            logger.warning(f"Event not found with slug: {self.kwargs['slug']}")
            raise
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get similar events for recommendations
        context['similar_events'] = self.object.get_similar_events()
        
        if self.request.user.is_authenticated:
            # Check if user is registered for this event
            try:
                registration = Registration.objects.get(
                    event=self.object,
                    attendee=self.request.user
                )
                context['is_registered'] = True
                context['registration_status'] = registration.status
            except Registration.DoesNotExist:
                context['is_registered'] = False
                context['registration_form'] = RegistrationForm()
            
            # Check if user is an organizer
            context['is_organizer'] = self.object.organizers.filter(id=self.request.user.id).exists()
        
        # Add registration stats
        context['registration_count'] = self.object.registrations.filter(status='confirmed').count()
        context['capacity_percentage'] = self.object.registration_percentage
        context['spots_left'] = self.object.spots_left
        
        # Add event status info
        now = timezone.now()
        context['is_upcoming'] = self.object.is_upcoming
        context['is_ongoing'] = self.object.is_ongoing
        context['is_past'] = self.object.is_past
        context['registration_open'] = self.object.registration_open
        
        return context


@login_required
def register_for_event(request, pk):
    if request.method != 'POST':
        return redirect('events:event_list')
    
    # Debug log
    logger.debug(f"Attempting to register for event with pk={pk}")
    
    try:
        # Retrieve the event
        event = get_object_or_404(Event, pk=pk)
        
        # Check if the event is published or if the user is an organizer or staff
        if event.status != 'published' and not (request.user.is_staff or event.organizers.filter(id=request.user.id).exists()):
            logger.warning(f"Registration attempt for non-published event: {event.title} (status: {event.status})")
            messages.error(request, "The event you're trying to register for isn't published.")
            return redirect('events:event_list')
            
    except Http404:
        logger.warning(f"Registration attempt for non-existent event with pk={pk}")
        messages.error(request, "The event you're trying to register for doesn't exist.")
        return redirect('events:event_list')
    
    # Check if registration is open
    if not event.registration_open:
        messages.error(request, "Registration for this event is closed.")
        return redirect(event.get_absolute_url())
    
    # Check if event is full
    if event.is_full:
        messages.error(request, "This event has reached its capacity.")
        return redirect(event.get_absolute_url())
    
    # Check if user is already registered
    existing_registration = Registration.objects.filter(event=event, attendee=request.user).first()
    if existing_registration:
        messages.info(request, f"You're already registered for this event (status: {existing_registration.status}).")
        return redirect(event.get_absolute_url())
    
    # Process form data if provided
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        registration = form.save(commit=False)
        registration.event = event
        registration.attendee = request.user
        registration.status = 'confirmed'
        registration.save()
        
        messages.success(request, "You've successfully registered for this event!")
        logger.info(f"User {request.user.username} registered for event {event.title} (ID: {event.id})")
    else:
        # If the form has errors but we're still creating a basic registration
        try:
            registration = Registration.objects.create(
                event=event,
                attendee=request.user,
                status='confirmed'
            )
            messages.success(request, "You've successfully registered for this event!")
            logger.info(f"User {request.user.username} registered for event {event.title} (ID: {event.id})")
            
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            messages.error(request, "An error occurred during registration. Please try again.")
    
    return redirect(event.get_absolute_url())


@login_required
def unregister_from_event(request, pk):
    if request.method != 'POST':
        return redirect('events:event_list')
    
    event = get_object_or_404(Event, pk=pk)
    logger.debug(f"Attempting to unregister from event: {event.title} (ID: {event.id})")
    
    # Check if registration exists
    try:
        registration = Registration.objects.get(
            event=event,
            attendee=request.user
        )
        
        # Check if it's too late to cancel (optional business rule)
        now = timezone.now()
        if event.start_date <= now:
            messages.error(request, "You cannot cancel registration for an event that has already started.")
            return redirect(event.get_absolute_url())
        
        # Delete registration
        registration.delete()
        messages.success(request, "Your registration has been canceled.")
        logger.info(f"User {request.user.username} unregistered from event {event.title} (ID: {event.id})")
        
    except Registration.DoesNotExist:
        logger.warning(f"Unregistration attempt for non-registered user: {request.user.username}, event: {event.title}")
        messages.error(request, "You are not registered for this event.")
    
    return redirect(event.get_absolute_url())


def calendar_events_json(request):
    """View to provide event data for calendar display"""
    # Get published events
    events = Event.objects.filter(status='published')
    
    # Filter for date range if provided
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start and end:
        events = events.filter(
            Q(start_date__range=[start, end]) | 
            Q(end_date__range=[start, end]) |
            Q(start_date__lte=start, end_date__gte=end)
        )
    
    # Format events for calendar
    calendar_events = []
    for event in events:
        calendar_events.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'url': event.get_absolute_url(),
            'allDay': (event.end_date - event.start_date).days > 0,
            'className': 'bg-primary' if event.is_virtual else 'bg-success'
        })
    
    return JsonResponse(calendar_events, safe=False)


class ManageAttendeesView(LoginRequiredMixin, DetailView):
    """View for organizers to manage event attendees"""
    model = Event
    template_name = 'events/manage_attendees.html'
    context_object_name = 'event'
    
    def get_queryset(self):
        # Only allow organizers to access this view
        return Event.objects.filter(organizers=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all registrations for this event with related user data
        registrations = Registration.objects.filter(
            event=self.object
        ).select_related('attendee').order_by('status', 'registration_date')
        
        # Group registrations by status
        context['confirmed_registrations'] = registrations.filter(status='confirmed')
        context['pending_registrations'] = registrations.filter(status='pending')
        context['canceled_registrations'] = registrations.filter(status='canceled')
        context['attended_registrations'] = registrations.filter(status='attended')
        context['waitlisted_registrations'] = registrations.filter(status='waitlisted')
        
        # Registration stats
        context['total_registrations'] = registrations.count()
        context['registration_percentage'] = self.object.registration_percentage
        context['spots_left'] = self.object.spots_left
        
        return context


@login_required
def check_in_attendee(request, event_id, registration_id):
    """Mark an attendee as present at the event"""
    # Verify user is an organizer
    event = get_object_or_404(Event, id=event_id, organizers=request.user)
    
    # Get the registration
    registration = get_object_or_404(Registration, id=registration_id, event=event)
    
    # Mark as attended
    registration.mark_as_attended()
    
    messages.success(request, f"{registration.attendee.get_full_name()} has been checked in.")
    return redirect('events:manage_attendees', pk=event_id)


# class EventCreateView(LoginRequiredMixin, CreateView):
#     model = Event
#     form_class = EventForm
#     template_name = 'events/event_form.html'
    
#     def form_valid(self, form):
#         # Set initial status to draft
#         form.instance.status = 'draft'
        
#         # Save the form to get an instance with ID
#         response = super().form_valid(form)
        
#         # Add the current user as an organizer
#         form.instance.organizers.add(self.request.user)
        
#         # Log successful creation
#         logger.info(f"Event created: {form.instance.title} (ID: {form.instance.id}, slug: {form.instance.slug})")
        
#         messages.success(self.request, "Event created successfully! It will be published after review.")
#         return response
    
#     def get_success_url(self):
#         return self.object.get_absolute_url()

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Check if categories exist, create some if not
        if EventCategory.objects.count() == 0:
            EventCategory.objects.create(name="Workshop", slug="workshop", description="Hands-on learning sessions")
            EventCategory.objects.create(name="Conference", slug="conference", description="Large formal gathering")
            EventCategory.objects.create(name="Webinar", slug="webinar", description="Online educational event")
        
        return form

    def form_valid(self, form):
        # Only set status to draft if not specified by the user
        if not form.instance.status:
            form.instance.status = 'draft'
        
        # Save the form to get an instance with ID
        response = super().form_valid(form)
        
        # Add the current user as an organizer
        form.instance.organizers.add(self.request.user)
        
        # Log successful creation
        logger.info(f"Event created: {form.instance.title} (ID: {form.instance.id}, slug: {form.instance.slug})")
        
        if form.instance.status == 'published':
            messages.success(self.request, "Event published successfully!")
        else:
            messages.success(self.request, "Event created successfully! It will be published after review.")
            
        return response
    
    def get_success_url(self):
        return self.object.get_absolute_url()


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def get_queryset(self):
        # Only allow organizers or staff to edit events
        if self.request.user.is_staff:
            return Event.objects.all()
        return Event.objects.filter(organizers=self.request.user)
    
    def form_valid(self, form):
        # Log the update attempt
        logger.info(f"Updating event: {form.instance.title} (ID: {form.instance.id})")
        
        response = super().form_valid(form)
        messages.success(self.request, "Event updated successfully!")
        return response
    
    def get_success_url(self):
        return self.object.get_absolute_url()


def apple_calendar_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    cal = Calendar()
    cal_event = ICalEvent()
    cal_event.add('summary', event.title)
    cal_event.add('dtstart', event.start_date)
    cal_event.add('dtend', event.end_date)
    cal_event.add('description', event.description)
    cal_event.add('location', event.location)
    cal.add_component(cal_event)
    
    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="{event.title}.ics"'
    return response

def outlook_calendar_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    from icalendar import Calendar, Event as ICalEvent
    from datetime import datetime
    import uuid
    
    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//Your Organization//Event Calendar//EN')
    cal.add('version', '2.0')
    
    # Create event
    ical_event = ICalEvent()
    
    # Add event properties
    ical_event.add('summary', event.title)
    ical_event.add('description', event.description)
    ical_event.add('location', event.location)
    
    # Add start and end times
    ical_event.add('dtstart', event.start_date)
    ical_event.add('dtend', event.end_date)
    
    # Add creation time
    ical_event.add('dtstamp', datetime.utcnow())
    
    # Add UID
    ical_event.add('uid', str(uuid.uuid4()))
    
    # Add event to calendar
    cal.add_component(ical_event)
    
    # Create response
    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="{event.title}.ics"'
    
    return response