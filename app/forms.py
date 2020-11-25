from django import forms
from app.models import Question

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, 
        widget=forms.TextInput(attrs={
            'class': 'right-col form-control col-sm-6',
            'placeholder': 'Enter your Username here',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'right-col form-control col-sm-6',
            'placeholder': '********',
            }
        )
    )

class AskForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'text']
        