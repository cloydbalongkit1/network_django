from django import forms

class EditProfile(forms.Form):
    
    first_name = forms.CharField(max_length=100, required=True, 
                                 widget=forms.TextInput(attrs={
                                     'class': 'form-control', 
                                     }))
    
    last_name = forms.CharField(max_length=100, required=True, 
                                widget=forms.TextInput(attrs={
                                    'class': 'form-control',
                                    }))
    
    bio = forms.CharField(max_length=250, required=True,
                          widget=forms.TextInput(attrs={
                              'class': 'form-control', 
                              }))
    
    location = forms.CharField(max_length=100, required=True,
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control', 
                                   }))
    
    work = forms.CharField(max_length=100, required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control', 
                               }))
