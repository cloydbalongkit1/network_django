from django import forms
from .models import User

class EditProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'location', 'work']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your bio', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your location'}),
            'work': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your work'}),
        }



class EditPost(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control', 
                'placeholder': 'Edit your post', 
                'rows': 5,
                'id': 'editContent',
            }
        ),
        label="Edit Post"
    )