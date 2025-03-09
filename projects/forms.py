from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'github_link', 'tech_stack', 'image', 'is_seeking_collaborators']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter project description'}),  # Simple textarea
            'github_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'GitHub Repository URL'}),
            'tech_stack': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Python, Django, React'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_seeking_collaborators': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
