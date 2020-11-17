from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.db.models.query import QuerySet
from app.models import Profile, Question, Answer, AnswerLike
from django.contrib.auth.models import User

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def getBaseProfile():
    if not Profile.objects.filter(nickname='basicNick').exists():
        if not User.objects.filter(username='basic').exists():
            User.objects.create_user(
                'basic',
                'Toba.ru@mail.ru',
                'thisismyhair')
        Profile.objects.create(
            user=User.objects.get(username='basic'),
            avatar='avatars/' + 'image1.jpg',
            nickname='basicNick'
        )
    return Profile.objects.get(user__username='basic')

def getBaseDict(logged_in=True):
    profile = getBaseProfile()
    profile_dict = {
        'user': profile.user,
        'avatar': profile.avatar,
        'nickname': profile.nickname,
    }
    
    profile_dict.update({'logged_in': logged_in})
    return profile_dict

def CheckIfLiked(user, post_or_posts):
    if isinstance(post_or_posts, (Question, Answer)):
        result = model_to_dict(post_or_posts)

        # Replacing author field with actual author instead of an ID.
        result['author'] = post_or_posts.author

        if isinstance(post_or_posts, Question):
            # Replacing tags field with actual tags.
            result['tags'] = post_or_posts.tags

            # Adding amount of answers.
            result['answers_amount'] = post_or_posts.answers.count()

        # Adding whether or not user liked/disliked that post.
        result['liked_or_disliked'] =  user.LikedOrDisliked(post_or_posts)
        result['rating'] = post_or_posts.rating
        return result

    elif isinstance(post_or_posts, QuerySet):
        if not post_or_posts.exists():
            return []

        if isinstance(post_or_posts[0], (Question, Answer)):
            return [CheckIfLiked(user, post) for post in post_or_posts]
    raise TypeError('Argument post_or_posts must be either Question, Answer or QuerySet of them')

def index(request):
    page = paginate(CheckIfLiked(getBaseProfile(),
                                 Question.objects.New().all().prefetch_related(
                                     'author', 'tags', 'likes'
                                     )
                                ),
                    request, 5)
    return render(request, 'index.html', {
        'page': page,
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': getBaseDict(logged_in=True),
    })

def question(request, id):
    try:
        question = Question.objects.get(id=id)
        answers = question.answers.Best().all().prefetch_related('likes')
        return render(request, 'question.html', {
            'question': CheckIfLiked(getBaseProfile(), question),
            'page': paginate(CheckIfLiked(getBaseProfile(), answers), request, 5),
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
    questions_query = Question.objects.HotWithTag(tag).all().prefetch_related(
                          'author', 'tags', 'likes'
                      )
    page = paginate(CheckIfLiked(getBaseProfile(), questions_query), request, 5)
    return render(request, 'tag.html', {
        'page': page,
        'page_end_diff': page.paginator.num_pages - page.number,
        'tag': tag,
        'user': getBaseDict(logged_in=True),
    })

def hot(request):
    questions_query = Question.objects.Hot().all().prefetch_related(
                          'author', 'tags', 'likes'
                      )
    page = paginate(CheckIfLiked(getBaseProfile(), questions_query), request, 5)
    return render(request, 'hot_questions.html', {
        'page': page,
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': getBaseDict(logged_in=True),
    })
