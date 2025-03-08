# forms.py
from django import forms
from .models import Event, Registration, EventCategory

class EventForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=EventCategory.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2',
            'id': 'id_categories_select2'
        }),
        required=False
    )
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'short_description', 
            'start_date', 'end_date', 'registration_deadline', 
            'location', 'is_virtual', 'virtual_link', 
            'image', 'capacity', 'categories', 'status'
        ]
        # Remove 'status' from fields list for non-admin users
        
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 6}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        registration_deadline = cleaned_data.get('registration_deadline')
        
        # Validate that end date is after start date
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'End date must be after start date.')
        
        # Validate registration deadline
        if registration_deadline and start_date and registration_deadline > start_date:
            self.add_error('registration_deadline', 'Registration deadline must be before event start date.')
        
        return cleaned_data


class AdminEventForm(EventForm):
    """Form for admin users that includes additional fields"""
    class Meta(EventForm.Meta):
        fields = EventForm.Meta.fields + ['status']
    
# forms.py - Registration forms
from django import forms
from .models import Registration

class RegistrationForm(forms.ModelForm):
    """Form for basic registration"""
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special requirements or notes?'}),
        required=False,
        label="Notes"
    )
    
    class Meta:
        model = Registration
        fields = ['notes']  # We'll set event and user in the view
        
    def clean(self):
        """Additional form validation if needed"""
        cleaned_data = super().clean()
        # You can add custom validation here if needed
        return cleaned_data


class RegistrationAdminForm(forms.ModelForm):
    """Form for admins to manage registrations"""
    class Meta:
        model = Registration
        fields = ['status', 'notes', 'check_in_time']
        widgets = {
            'check_in_time': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }