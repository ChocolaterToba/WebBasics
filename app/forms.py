from django import forms
from app.models import Question, Answer, Tag
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='Login',
        widget=forms.TextInput(attrs={
            'class': 'right-col form-control',
            'placeholder': 'Enter your login here',
            }
        )
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'right-col form-control',
            'placeholder': '********',
            }
        )
    )


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'right-col form-control',
            'placeholder': '********',
            }
        )
    )
    password2 = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput(attrs={
            'class': 'right-col form-control',
            'placeholder': '********',
            }
        )
    )

    nickname = forms.CharField(
        max_length=30,
        label='Nickname',
        widget=forms.TextInput(attrs={
            'class': 'right-col form-control',
            'placeholder': 'Example Nick',
            }
        )
    )

    avatar = forms.ImageField(
        required=False,
        label='Avatar',
        widget=forms.ClearableFileInput(attrs={
            'id': 'avatar_id',
            'class': 'right-col form-control',
            'onchange': "sub(this, 'file_button_{}')".format('avatar_id'),
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        labels = {
            'username': 'Login',
            'email': 'Email',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'right-col form-control',
                'placeholder': 'Example Login',
                }
            ),
            'email': forms.EmailInput(attrs={
                'class': 'right-col form-control',
                'placeholder': 'Example@email.com',
                }
            ),
        }


class SettingsForm(forms.Form):
    username = forms.CharField(
        required=False, max_length=150,
        label='Login',
        widget=forms.TextInput(attrs={
            'class': 'right-col form-control',
            }
        )
    )

    email = forms.EmailField(
        required=False,
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'right-col form-control',
            }
        )
    )

    nickname = forms.CharField(
        required=False, max_length=30,
        label='Nickname',
        widget=forms.TextInput(attrs={
            'class': 'right-col form-control',
            }
        )
    )

    avatar = forms.ImageField(
        required=False,
        label='Avatar',
        widget=forms.ClearableFileInput(attrs={
            'id': 'avatar_id',
            'class': 'right-col form-control',
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
            self.fields['nickname'].widget.attrs['placeholder'] = \
                user.profile.nickname

        else:
            super(SettingsForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(SettingsForm, self).clean()

        username = cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            self.add_error('username', 'This username is already taken.')

        return cleaned_data


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        required=False, max_length=200,
        label='Tags (10 max)',
        widget=forms.TextInput(attrs={
            'class': 'right-col form-control',
            'placeholder': 'Enter your tags, separated by whitespace',
            }
        )
    )

    class Meta:
        model = Question
        fields = ['title', 'text']
        labels = {
            'title': 'Title',
            'text': 'Text',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'right-col form-control',
                'placeholder': "Enter question's title here",
                }
            ),
            'text': forms.Textarea(attrs={
                'class': 'right-col form-control',
                'placeholder': 'Enter you question here',
                'rows': '10',
                }
            ),
        }
    
    def clean(self):
        cleaned_data = super(QuestionForm, self).clean()

        if len(cleaned_data.get('tags').split(' ')) > 10:
            self.add_error('tags', 'Cannot add more than 10 tags.')
        return cleaned_data


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
