from django.contrib import admin
from .models import Event, EventCategory, Registration

# admin.py
from django.contrib import admin
from .models import Event, EventCategory, Registration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'status', 'is_virtual', 'created')
    list_filter = ('status', 'is_virtual', 'start_date', 'end_date', 'categories')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'
    filter_horizontal = ('categories', 'organizers')
    readonly_fields = ('created', 'updated')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'status')
        }),
        ('Date and Time', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Location', {
            'fields': ('location', 'is_virtual', 'virtual_link')
        }),
        ('Additional Info', {
            'fields': ('image', 'capacity', 'categories', 'organizers')
        }),
        ('System Info', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'attendee', 'registration_date', 'status')
    list_filter = ('status', 'registration_date')
    search_fields = ('event__title', 'attendee__username')
    ordering = ('-registration_date',)
    raw_id_fields = ('event', 'attendee')