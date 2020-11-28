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


def CheckIfLikedPost(user: User, post: Union[Question, Answer]):
    result = model_to_dict(post)

    # Replacing author field with actual author instead of IDs.
    result['author'] = post.author

    if isinstance(post, Question):

        # Adding amount of answers.
        result['answers_amount'] = post.answers.count()

    # Adding whether or not user liked/disliked that post.
    if user.is_authenticated:
        result['liked_or_disliked'] = post.LikedOrDislikedBy(user.profile)
    else:
        result['Liked_or_disliked'] = 'NoVote'
    return result


def CheckIfLikedPage(user: User, page: Page):
    page.object_list = [CheckIfLikedPost(user, post)
                        for post in page.object_list]
    return page


def index(request):
    questions = Question.objects.New().all().prefetch_related(
                    'author', 'tags', 'likes'
                )
    page = paginate(questions, request, 5)

    return render(request, 'index.html', {
        'page': CheckIfLikedPage(request.user, page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': request.user,
        }
    )


def question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        answers = question.answers.Best().all().prefetch_related('likes')
        answers_page = paginate(answers, request, 5)

        if not request.user.is_authenticated:
            return render(request, 'question.html', {
                'question': CheckIfLikedPost(request.user, question),
                'page': CheckIfLikedPage(request.user, answers_page),
                'user': request.user,
                'form': AnswerForm(),
                }
            )

        if request.method == 'POST':
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer = Answer.objects.create(
                    author_id=request.user.profile.id,
                    related_question_id=question_id,
                    text=form.cleaned_data['text']
                )

                response = redirect('question', question_id=question_id)
                response['Location'] += '#answer{}'.format(answer.id)
                return response

            return render(request, 'question.html', {
                'question': CheckIfLikedPost(request.user, question),
                'page': CheckIfLikedPage(request.user, answers_page),
                'user': request.user,
                'form': form,
                'error': 'Wrong answer input',  # TODO.
                }
            )

        else:
            return render(request, 'question.html', {
                'question': CheckIfLikedPost(request.user, question),
                'page': CheckIfLikedPage(request.user, answers_page),
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
    next_page = request.GET.get('continue', default='index')

    if request.user.is_authenticated:
        return redirect(next_page)

    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile created by the signal

            if form.cleaned_data['avatar'] is not None:
                # Else avatar is Toba's (my dog's) photo.
                user.profile.avatar = form.cleaned_data['avatar']

            user.profile.nickname = form.cleaned_data['nickname']
            user.save()

            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            auth_login(request, user)
            return redirect(next_page)
        print(form)

        return render(request, 'signup.html', {
            'user': request.user,
            'form': form,
            }
        )
    else:
        return render(request, 'signup.html', {
            'user': request.user,
            'form': SignUpForm(),
            }
        )


def login(request):
    next_page = request.GET.get('continue', default='index')

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
            else:
                form.add_error(None, 'Incorrect login or password')
        
        print(form.errors)

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
    next_page = request.GET.get('continue', default='index')
    auth_logout(request)
    return redirect(next_page)


def settings(request):
    if not request.user.is_authenticated:
        response = redirect('login')
        response['Location'] += '?continue=/settings/'
        return response

    user = request.user

    initial_form_data = {
        'username': user.username,
        'email': user.email,
        'nickname': user.profile.nickname,
        'avatar': user.profile.avatar,
    }

    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES,
                            user=user, initial=initial_form_data)
        if form.is_valid():
            if 'username' in form.changed_data:
                user.username = form.cleaned_data['username']
            if 'email' in form.changed_data:
                user.email = form.cleaned_data['email']
            if 'nickname' in form.changed_data:
                user.profile.nickname = form.cleaned_data['nickname']
            if 'avatar' in form.changed_data:
                user.profile.avatar = form.cleaned_data['avatar']
            user.save()
            return render(request, 'settings.html', {
                'user': user,
                'form': form,
                }
            )

        return render(request, 'settings.html', {
            'user': user,
            'form': form,
            'error': 'Wrong settings input',  # TODO.
            }
        )
    else:
        return render(request, 'settings.html', {
            'user': user,
            'form': SettingsForm(user=user),
            }
        )


def tag(request, tag):
    questions = Question.objects.HotWithTag(tag).all().prefetch_related(
                    'author', 'tags', 'likes'
                )
    page = paginate(questions, request, 5)
    return render(request, 'tag.html', {
        'page': CheckIfLikedPage(request.user, page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': request.user,
        'tag': tag,
        }
    )


def hot(request):
    questions = Question.objects.Hot().all().prefetch_related(
                    'author', 'tags', 'likes'
                )
    page = paginate(questions, request, 5)
    return render(request, 'hot_questions.html', {
        'page': CheckIfLikedPage(request.user, page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': request.user,
        }
    )
