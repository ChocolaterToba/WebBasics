from django import forms
from app.models import Question, Answer, Tag

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
        