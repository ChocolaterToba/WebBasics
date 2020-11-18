from typing import Union

from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, Page
from django.forms.models import model_to_dict
from django.db.models.query import QuerySet

from app.models import Profile, Question, Answer
from django.contrib.auth.models import User


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
            'password': 'thisismyhair'
        }
    )
    base_profile, created = Profile.objects.get_or_create(
        user_id=base_user.id,
        defaults={
            'user_id': base_user.id,
            'avatar': 'avatars/image1.jpg',
            'nickname': 'basicNick'
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
    result['liked_or_disliked'] = post.LikedOrDislikedBy(user)
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
    return render(request, 'index.html', {
        'page': CheckIfLiked(getBaseProfile(), page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': getBaseDict(logged_in=True),
    })

def question(request, id):
    try:
        question = Question.objects.get(id=id)
        answers = question.answers.Best().all().prefetch_related('likes')
        answer_page = paginate(answers, request, 5)
        return render(request, 'question.html', {
            'question': CheckIfLiked(getBaseProfile(), question),
            'page': CheckIfLiked(getBaseProfile(), answer_page),
            'user': getBaseDict(logged_in=True),
        })
    except:
        return render(request, '404.html', {
            'user': getBaseDict(logged_in=True),
        })

def ask(request):
    return render(request, 'ask.html', {
        'user': getBaseDict(logged_in=True),
    })

def signup(request):
    return render(request, 'signup.html', {
        'user': getBaseUser(logged_in=False),
    })

def login(request):
    return render(request, 'login.html', {
        'user': getBaseDict(logged_in=False),
    })

def settings(request):
    return render(request, 'settings.html', {
        'user': getBaseDict(logged_in=True),
    })

def tag(request, tag):
    questions = Question.objects.HotWithTag(tag).all().prefetch_related(
                    'author', 'tags', 'likes'
                )
    page = paginate(questions, request, 5)
    return render(request, 'index.html', {
        'page': CheckIfLiked(getBaseProfile(), page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': getBaseDict(logged_in=True),
    })

def hot(request):
    questions = Question.objects.Hot().all().prefetch_related(
                    'author', 'tags', 'likes'
                )
    page = paginate(questions, request, 5)
    return render(request, 'index.html', {
        'page': CheckIfLiked(getBaseProfile(), page),
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': getBaseDict(logged_in=True),
    })
