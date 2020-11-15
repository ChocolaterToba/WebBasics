from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.db.models.query import QuerySet
from app.models import Profile, Question, Answer

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

base_user = Profile.objects.get(id=1)
base_user_dict = {
    'user': base_user.user,
    'avatar': base_user.avatar,
    'nickname': base_user.nickname,
}

logged_in_user = base_user_dict.copy()
logged_in_user.update({'logged_in': True})

unlogged_in_user = base_user_dict.copy()
unlogged_in_user.update({'logged_in': False})

def CheckIfLiked(user, posts):
    if isinstance(posts, (Question, Answer)):
        result = model_to_dict(posts)
        result['liked_or_disliked'] =  user.LikedOrDisliked(posts)
        return result
    elif isinstance(posts, QuerySet):
        if not posts.exists():
            return []
        if isinstance(posts[0], (Question, Answer)):
            print(CheckIfLiked(user, posts[0]))
            return [CheckIfLiked(user, post) for post in posts]
    raise TypeError('Argument posts must be either Question, Answer or QuerySet of them')

def index(request):
    page = paginate(Question.objects.New().all().prefetch_related('author', 'answers', 'tags', 'likes'), request, 5)
    return render(request, 'index.html', {
        'page': page,
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': logged_in_user,
    })

def question(request, id):
    try:
        question = Question.objects.get(id=id)
        return render(request, 'question.html', {
            'question': CheckIfLiked(base_user, question),
            'answers': CheckIfLiked(base_user, question.answers.Best().all()),
            'user': logged_in_user,
        })
    except:
        return render(request, '404.html', {
            'user': logged_in_user,
        })

def ask(request):
    return render(request, 'ask.html', {
        'user': logged_in_user,
    })

def signup(request):
    return render(request, 'signup.html', {
        'user': unlogged_in_user,
    })

def login(request):
    return render(request, 'login.html', {
        'user': unlogged_in_user,
    })

def settings(request):
    return render(request, 'settings.html', {
        'user': logged_in_user,
    })

def tag(request, tag):
    page = paginate(Question.objects.SearchByTag(tag).all(),  request, 5)
    return render(request, 'tag.html', {
        'page': page,
        'page_end_diff': page.paginator.num_pages - page.number,
        'tag': tag,
        'user': logged_in_user,
    })

def hot(request):
    page = paginate(Question.objects.Hot().all(), request, 5)
    return render(request, 'hot_questions.html', {
        'page': page,
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': logged_in_user,
    })
