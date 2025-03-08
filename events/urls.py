# urls.py
from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [

    # Event list and detail views
    path('', views.EventListView.as_view(), name='event_list'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('edit/<int:pk>/', views.EventUpdateView.as_view(), name='event_edit'),
    
    # Registration views
    path('register/<int:pk>/', views.register_for_event, name='event_register'),
    path('unregister/<int:pk>/', views.unregister_from_event, name='event_unregister'),
    
    # Calendar data
    path('calendar-data/', views.calendar_events_json, name='calendar_data'),
    path('calendar/apple/<int:event_id>/', views.apple_calendar_event, name='apple_calendar_event'),
    path('calendar/outlook/<int:event_id>/', views.outlook_calendar_event, name='outlook_calendar_event'),
    
    # This should be last to avoid conflicts with other URL patterns
    path('<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    
    # Optional: Attendee management for organizers
    path('manage-attendees/<int:pk>/', views.ManageAttendeesView.as_view(), name='manage_attendees'),
    path('check-in/<int:event_id>/<int:registration_id>/', views.check_in_attendee, name='check_in_attendee'),
]