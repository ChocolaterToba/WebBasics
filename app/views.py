from typing import Union

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, Page

from django.forms.models import model_to_dict
from django.db.models.query import QuerySet

from app.models import Profile, Question, Answer
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout

from app.forms import *

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def getBaseProfile():
    base_user, created = User.objects.get_or_create(
        username='basic',
        defaults={
            'username': 'basic',
            'email': 'Example@mail.ru',
            'password': make_password('thisismyhair'),
        }
    )
    base_profile, created = Profile.objects.get_or_create(
        user_id=base_user.id,
        defaults={
            'user_id': base_user.id,
            'avatar': 'avatars/image1.jpg',
            'nickname': 'basicNick',
        }
    )

    return base_profile

def getBaseDict(logged_in=True):
    profile_dict = model_to_dict(getBaseProfile())
    profile_dict.update({'logged_in': logged_in})
    return profile_dict

def CheckIfLikedInner(user: User, post: Union[Question, Answer]):
    result = model_to_dict(post)

    # Replacing author field with actual author instead of IDs.
    result['author'] = post.author

    if isinstance(post, Question):

        # Adding amount of answers.
        result['answers_amount'] = post.answers.count()

    # Adding whether or not user liked/disliked that post.
    if user.is_authenticated:
        result['liked_or_disliked'] = post.LikedOrDislikedBy(user.profile)
    return result

def CheckIfLiked(user, post_posts_page):
    if isinstance(post_posts_page, QuerySet):
        return [CheckIfLikedInner(user, post)
                for post in post_posts_page]
    if isinstance(post_posts_page, Page):
        post_posts_page.object_list = CheckIfLiked(user, post_posts_page.object_list)
        return post_posts_page
    return CheckIfLikedInner(user, post_posts_page)


def index(request):
    questions = Question.objects.New().all().prefetch_related(
                    'author', 'tags', 'likes'
                )
    page = paginate(questions, request, 5)

    user = request.user

    return render(request, 'index.html', {
        'page': CheckIfLiked(user, page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': user,
        }
    )

def question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        answers = question.answers.Best().all().prefetch_related('likes')
        answer_page = paginate(answers, request, 5)

        if not request.user.is_authenticated:
            return render(request, 'question.html', {
            'question': CheckIfLiked(request.user, question),
            'page': CheckIfLiked(request.user, answer_page),
            'user': request.user,
            'form': AnswerForm(),
            }
        )

        if request.method == 'POST':
            form = AnswerForm(request.POST)
            if form.is_valid():
                Answer.objects.create(
                    author_id=request.user.profile.id,
                    related_question_id = question_id,
                    text=form.cleaned_data['text']
                )
                return redirect('question', question_id=question_id)  # TODO: add answer's id

            return render(request, 'question.html', {
                'question': CheckIfLiked(request.user, question),
                'page': CheckIfLiked(request.user, answer_page),
                'user': request.user,
                'form': form,
                'error': 'Wrong answer input',  # TODO.
                }
            )

        else:
            return render(request, 'question.html', {
                'question': CheckIfLiked(request.user, question),
                'page': CheckIfLiked(request.user, answer_page),
                'user': request.user,
                'form': AnswerForm(),
                }
            )
    except:
        return render(request, '404.html', {
            'user': request.user,
            }
        )

def ask(request):
    if not request.user.is_authenticated:
        response = redirect('login')
        response['Location'] += '?continue=/ask/'
        return response

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = Question(
                author_id=request.user.profile.id,
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text'],
            )
            question.save()
            question.tags.set(form.cleaned_data['tags'])
            return redirect('question', id=question.id)

        return render(request, 'ask.html', {
            'user': request.user,
            'form': form,
            'error': 'Wrong question input',  # TODO.
            }
        )

    else:
        return render(request, 'ask.html', {
            'user': request.user,
            'form': QuestionForm(),
            }
        )

def signup(request):
    return render(request, 'signup.html', {
        'user': request.user,
        }
    )

def login(request):
    next_page = request.GET.get('continue', default='/index/')

    if request.user.is_authenticated:
        return redirect(next_page)

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                auth_login(request, user)
                return redirect(next_page)
        
        return render(request, 'login.html', {
            'user': request.user,
            'form': form,
            'error': 'Error during login',  # TODO.
            }
        )

    else:
        form = LoginForm()
        return render(request, 'login.html', {
            'user': request.user,
            'form': form,
            }
        )

def logout(request):
    next_page = request.GET.get('continue', default='/index/')
    auth_logout(request)
    return redirect(next_page)

def settings(request):
    return render(request, 'settings.html', {
        'user': request.user,
        }
    )

def tag(request, tag):
    questions = Question.objects.HotWithTag(tag).all().prefetch_related(
                    'author', 'tags', 'likes'
                )
    page = paginate(questions, request, 5)
    return render(request, 'index.html', {
        'page': CheckIfLiked(getBaseProfile(), page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': request.user,
        }
    )

def hot(request):
    questions = Question.objects.Hot().all().prefetch_related(
                    'author', 'tags', 'likes'
                )
    page = paginate(questions, request, 5)
    return render(request, 'index.html', {
        'page': CheckIfLiked(getBaseProfile(), page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': request.user,
        }
    )
