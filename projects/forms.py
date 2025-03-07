from django import forms
from .models import Project, Comment

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'github_link', 'tech_stack', 'image', 'is_seeking_collaborators']
        widgets = {
            'tech_stack': forms.TextInput(attrs={'placeholder': 'e.g., Python, Django, React'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
