from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.db.models.query import QuerySet
from app.models import Profile, Question, Answer
from django.contrib.auth.models import User

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

# base_user_user = User.objects.create_user(
#                 'firstname',
#                 'email@mail.ru',
#                 'thisismyhair')
base_user = Profile.objects.first()
base_user_dict = {
    'user': base_user.user,
    'avatar': base_user.avatar,
    'nickname': base_user.nickname,
}

logged_in_user = base_user_dict.copy()
logged_in_user.update({'logged_in': True})

unlogged_in_user = base_user_dict.copy()
unlogged_in_user.update({'logged_in': False})

def CheckIfLiked(user, post_or_posts):
    if isinstance(post_or_posts, (Question, Answer)):
        result = model_to_dict(post_or_posts)

        # Replacing author field with actual author instead of an ID.
        result['author'] = post_or_posts.author

        if isinstance(post_or_posts, Question):
            # Replacing tags field with actual tags.
            result['tags'] = post_or_posts.tags

            # Adding amount of answers.
            result['answers_amount'] = post_or_posts.AnswersAmount()

        # Adding whether or not user liked/disliked that post.
        result['liked_or_disliked'] =  user.LikedOrDisliked(post_or_posts)
        return result

    elif isinstance(post_or_posts, QuerySet):
        if not post_or_posts.exists():
            return []

        if isinstance(post_or_posts[0], (Question, Answer)):
            return [CheckIfLiked(user, post) for post in post_or_posts]
    raise TypeError('Argument post_or_posts must be either Question, Answer or QuerySet of them')

def index(request):
    page = paginate(CheckIfLiked(base_user,
                                 Question.objects.New().all().prefetch_related(
                                     'author', 'tags', 'likes'
                                     )
                                ),
                    request, 5)
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
    page = paginate(CheckIfLiked(base_user,
                                 Question.objects.SearchByTag(tag).all().prefetch_related(
                                     'author', 'tags', 'likes'
                                     )
                                ),
                    request, 5)
    return render(request, 'tag.html', {
        'page': page,
        'page_end_diff': page.paginator.num_pages - page.number,
        'tag': tag,
        'user': logged_in_user,
    })

def hot(request):
    page = paginate(CheckIfLiked(base_user,
                                 Question.objects.Hot().all().prefetch_related(
                                     'author', 'tags', 'likes'
                                     )
                                ),
                    request, 5)
    return render(request, 'hot_questions.html', {
        'page': page,
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': logged_in_user,
    })
