from django import forms
from .models import Category, Topic, Post

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Topic Title'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control md-editor',
                'rows': 8, 
                'placeholder': 'Write your post content here...\n\nMarkdown is supported.',
                'required': True,
                # Don't set style here - we'll handle that in JS to keep it focusable
            }),
        }
        labels = {
            'content': 'Message',
        }
