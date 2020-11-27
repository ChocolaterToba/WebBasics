from django import forms
from app.models import Question, Answer, Tag
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, 
        widget=forms.TextInput(attrs={
            'class': 'right-col form-control col-sm-6',
            'placeholder': 'Enter your login here',
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

class SignUpForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'right-col form-control col-sm-6',
            'placeholder': '********',
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'right-col form-control col-sm-6',
            'placeholder': '********',
            }
        )
    )

    avatar = forms.ImageField(required=False,
        widget=forms.ClearableFileInput(attrs={
            'id': 'avatar_id',
            'class': 'right-col form-control col-sm-6',
            'onchange': "sub(this, 'file_button_{}')".format('avatar_id'),
            }
        )
    )

    nickname = forms.CharField(max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'right-col form-control col-sm-6',
            'placeholder': 'Example Nick',
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'right-col form-control col-sm-6',
                'placeholder': 'Example Login',
                }
            ),
            'email': forms.EmailInput(attrs={
                'class': 'right-col form-control col-sm-6',
                'placeholder': 'Example@email.com',
                }
            ),
        }

class SettingsForm(forms.Form):
    username = forms.CharField(required=False, max_length=150, 
        widget=forms.TextInput(attrs={
            'class': 'right-col form-control col-sm-6',
            }
        )
    )

    email = forms.EmailField(required=False,
        widget=forms.EmailInput(attrs={
            'class': 'right-col form-control col-sm-6',
            }
        )
    )

    nickname = forms.CharField(required=False, max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'right-col form-control col-sm-6',
            }
        )
    )

    avatar = forms.ImageField(required=False,
        widget=forms.ClearableFileInput(attrs={
            'id': 'avatar_id',
            'class': 'right-col form-control col-sm-6',
            'onchange': "sub(this, 'file_button_{}')".format('avatar_id'),
            }
        )
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs.pop('user')
            super(SettingsForm, self).__init__(*args, **kwargs)
            self.fields['username'].widget.attrs['placeholder'] = user.username
            self.fields['email'].widget.attrs['placeholder'] = user.email
            self.fields['nickname'].widget.attrs['placeholder'] = user.profile.nickname

        else:
            super(SettingsForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super(SettingsForm, self).clean()

        username = cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            self.add_error('username', 'This username is already taken.')

        return cleaned_data

class QuestionForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
                queryset=Tag.objects.all(),
                to_field_name="name",
            )

    class Meta:
        model = Question
        fields = ['title', 'text', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'right-col form-control col-sm-8 col-md-9',
                'placeholder': "Enter question's title here",
                }
            ),
            'text': forms.Textarea(attrs={
                'class': 'right-col form-control col-sm-8 col-md-9',
                'placeholder': 'Enter you question here',
                'rows': '10',
                }
            ),
            'tags': forms.SelectMultiple(attrs={
                'class': 'right-col form-control col-sm-8 col-md-9',
                }
            ),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'answer-block form-control',
                'placeholder': 'Enter you answer here',
                'rows': '4',
                }
            ),
        }
        