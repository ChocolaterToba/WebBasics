from typing import Union
from math import ceil

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator, Page

from AskAglicheev.settings import STATIC_URL

from django.forms.models import model_to_dict
from django.db.models.query import QuerySet
from django.db import transaction

from app.models import Profile, Question, Answer, QuestionLike, AnswerLike
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from app.forms import *


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def check_if_liked_post(user: User, post: Union[Question, Answer]):
    result = model_to_dict(post)

    # Replacing author field with actual author instead of IDs.
    result['author'] = post.author

    if isinstance(post, Question):

        # Adding amount of answers.
        result['answers_amount'] = post.answers.count()

    # Adding whether or not user liked/disliked that post.
    if user.is_authenticated:
        result['liked_or_disliked'] = post.liked_or_disliked_by(user.profile)
    else:
        result['Liked_or_disliked'] = 'NoVote'
    return result


def check_if_liked_page(user: User, page: Page):
    page.object_list = [check_if_liked_post(user, post)
                        for post in page.object_list]
    return page


def index(request):
    questions = Question.objects.new().all().prefetch_related(
                    'author', 'tags', 'likes'
                )
    page = paginate(questions, request, 5)

    return render(request, 'index.html', {
        'page': check_if_liked_page(request.user, page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': request.user,
        }
    )


def question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        answers = question.answers.best().all().prefetch_related('likes')
        page = paginate(answers, request, 5)

        if not request.user.is_authenticated:
            return render(request, 'question.html', {
                'question': check_if_liked_post(request.user, question),
                'page': check_if_liked_page(request.user, page),
                'page_end_diff': page.paginator.num_pages - page.number,
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

                page_number = 1
                answers = Question.objects.get(id=question_id).answers.best().all()
                for i, other_answer in enumerate(answers):
                    if other_answer == answer:
                        print(i, answer, other_answer)
                        page_number = int(i / 5) + 1
                        break

                return redirect(
                    reverse('question', args=[question_id]) +
                        '?page={}#answer{}'.format(page_number, answer.id)
                )

            return render(request, 'question.html', {
                'question': check_if_liked_post(request.user, question),
                'page': check_if_liked_page(request.user, page),
                'page_end_diff': page.paginator.num_pages - page.number,
                'user': request.user,
                'form': form,
                }
            )

        else:
            return render(request, 'question.html', {
                'question': check_if_liked_post(request.user, question),
                'page': check_if_liked_page(request.user, page),
                'page_end_diff': page.paginator.num_pages - page.number,
                'user': request.user,
                'form': AnswerForm(),
                }
            )
    except Exception as e:
        print(e)
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

            tags = list(set(form.cleaned_data['tags'].split(' ')))
            with transaction.atomic():
                for tag in tags:
                    if not Tag.objects.filter(name=tag).exists():
                        Tag.objects.create(name=tag)

            question.save()
            question.tags.set(tags)
            return redirect('question', question_id=question.id)

        return render(request, 'ask.html', {
            'user': request.user,
            'form': form,
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
            }
        )
    else:
        return render(request, 'settings.html', {
            'user': user,
            'form': SettingsForm(user=user),
            }
        )


def tag(request, tag):
    questions = Question.objects.hot_with_tag(tag).all().prefetch_related(
                    'author', 'tags', 'likes'
                )
    page = paginate(questions, request, 5)
    return render(request, 'tag.html', {
        'page': check_if_liked_page(request.user, page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': request.user,
        'tag': tag,
        }
    )


def hot(request):
    questions = Question.objects.hot().all().prefetch_related(
                    'author', 'tags', 'likes'
                )
    page = paginate(questions, request, 5)
    return render(request, 'hot_questions.html', {
        'page': check_if_liked_page(request.user, page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': request.user,
        }
    )

@require_POST
@login_required
def vote(request):
    data = request.POST
    if 'question_id' in data:
        question = Question.objects.get(id=data['question_id'])
        action = data['action']
        if action == 'like':
            like, created = QuestionLike.objects.get_or_create(
                user_id=request.user.profile.id,
                question_id=question.id,
            )
            if created:
                question.rating += 1
                question.save()
            elif like.is_a_like == QuestionLike.DISLIKE:
                question.rating += 2
                question.save()
            else:
                return JsonResponse({
                    'success': False,
                    'error': "Can't like question that is liked already",
                    },
                    status=500,
                )

            like.is_a_like = QuestionLike.LIKE
            like.save()
            return JsonResponse({
                'question_rating': question.rating,
                'like_src': STATIC_URL + 'img/caret-up-fill.svg',
                'like_action': 'unlike',
                'dislike_src': STATIC_URL + 'img/caret-down.svg',
                'dislike_action': 'dislike',
                }
            )

        elif action == 'undislike':
            dislike = QuestionLike.objects.filter(
                user_id=request.user.profile.id,
                question_id=question.id,
            )

            if dislike.exists():
                dislike = dislike.first()
                if dislike.is_a_like == QuestionLike.DISLIKE:
                    question.rating += 1
                    question.save()
                    dislike.delete()

                    return JsonResponse({
                        'question_rating': question.rating,
                        'dislike_src': STATIC_URL + 'img/caret-down.svg',
                        'dislike_action': 'dislike',
                        }
                    )

            return JsonResponse({
                'success': False,
                'error': "Can't undislike question that is not disliked",
                },
                status=500,
            )
        
        elif action == 'dislike':
            dislike, created = QuestionLike.objects.get_or_create(
                user_id=request.user.profile.id,
                question_id=question.id,
            )
            if created:
                question.rating -= 1
                question.save()
            elif dislike.is_a_like == QuestionLike.LIKE:
                question.rating -= 2
                question.save()
            else:
                return JsonResponse({
                    'success': False,
                    'error': "Can't dislike question that is disliked already",
                    },
                    status=500,
                )

            dislike.is_a_like = QuestionLike.DISLIKE
            dislike.save()
            return JsonResponse({
                'question_rating': question.rating,
                'like_src': STATIC_URL + 'img/caret-up.svg',
                'like_action': 'like',
                'dislike_src': STATIC_URL + 'img/caret-down-fill.svg',
                'dislike_action': 'undislike',
                }
            )

        else:
            like = QuestionLike.objects.filter(
                user_id=request.user.profile.id,
                question_id=question.id,
            )

            if like.exists():
                like = like.first()
                if like.is_a_like == QuestionLike.LIKE:
                    question.rating -= 1
                    question.save()
                    like.delete()

                    return JsonResponse({
                        'question_rating': question.rating,
                        'like_src': STATIC_URL + 'img/caret-up.svg',
                        'like_action': 'like',
                        }
                    )

            return JsonResponse({
                'success': False,
                'error': "Can't unlike question that is not liked",
                },
                status=500,
            )

    elif 'answer_id' in data:
        answer = Answer.objects.get(id=data['answer_id'])
        action = data['action']
        if action == 'like':
            like, created = AnswerLike.objects.get_or_create(
                user_id=request.user.profile.id,
                answer_id=answer.id,
            )
            if created:
                answer.rating += 1
                answer.save()
            elif like.is_a_like == AnswerLike.DISLIKE:
                answer.rating += 2
                answer.save()
            else:
                return JsonResponse({
                    'success': False,
                    'error': "Can't like answer that is liked already",
                    },
                    status=500,
                )

            like.is_a_like = AnswerLike.LIKE
            like.save()
            return JsonResponse({
                'answer_rating': answer.rating,
                'like_src': STATIC_URL + 'img/caret-up-fill.svg',
                'like_action': 'unlike',
                'dislike_src': STATIC_URL + 'img/caret-down.svg',
                'dislike_action': 'dislike',
                }
            )

        elif action == 'undislike':
            dislike = AnswerLike.objects.filter(
                user_id=request.user.profile.id,
                answer_id=answer.id,
            )

            if dislike.exists():
                dislike = dislike.first()
                if dislike.is_a_like == AnswerLike.DISLIKE:
                    answer.rating += 1
                    answer.save()
                    dislike.delete()

                    return JsonResponse({
                        'answer_rating': answer.rating,
                        'dislike_src': STATIC_URL + 'img/caret-down.svg',
                        'dislike_action': 'dislike',
                        }
                    )

            return JsonResponse({
                'success': False,
                'error': "Can't undislike answer that is not disliked",
                },
                status=500,
            )
        
        elif action == 'dislike':
            dislike, created = AnswerLike.objects.get_or_create(
                user_id=request.user.profile.id,
                answer_id=answer.id,
            )
            if created:
                answer.rating -= 1
                answer.save()
            elif dislike.is_a_like == AnswerLike.LIKE:
                answer.rating -= 2
                answer.save()
            else:
                return JsonResponse({
                    'success': False,
                    'error': "Can't dislike answer that is disliked already",
                    },
                    status=500,
                )

            dislike.is_a_like = AnswerLike.DISLIKE
            dislike.save()
            return JsonResponse({
                'answer_rating': answer.rating,
                'like_src': STATIC_URL + 'img/caret-up.svg',
                'like_action': 'like',
                'dislike_src': STATIC_URL + 'img/caret-down-fill.svg',
                'dislike_action': 'undislike',
                }
            )

        else:
            like = AnswerLike.objects.filter(
                user_id=request.user.profile.id,
                answer_id=answer.id,
            )

            if like.exists():
                like = like.first()
                if like.is_a_like == AnswerLike.LIKE:
                    answer.rating -= 1
                    answer.save()
                    like.delete()

                    return JsonResponse({
                        'answer_rating': answer.rating,
                        'like_src': STATIC_URL + 'img/caret-up.svg',
                        'like_action': 'like',
                        }
                    )

            return JsonResponse({
                'success': False,
                'error': "Can't unlike answer that is not liked",
                },
                status=500,
            )

@require_POST
@login_required
def mark_correct(request):
    data = request.POST
    print(data)
    # Maybe also add check for question's existence???
    question = Question.objects.get(id=data['question_id'])
    if question.author_id == request.user.profile.id:
        answer = question.answers.get(id=data['answer_id'])
        answer.is_correct = not answer.is_correct
        answer.save()
        return JsonResponse({
            'success': True,
            }
        )
    return JsonResponse({
            'success': False,
            'error': "Users can't check correct answers on other users' questions",
            },
            status=500,
        )
