from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from app.models import Question

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

logged_in_user = {
    'id': 123,
    'logged_in': True,
    'username': 'StandardUsername',
    'login': 'StandardLogin',
    'e_mail': 'Email@mail.ru',
}

unlogged_in_user = {
    'logged_in': False,
}

questions = []
for i in range(1, 60):
    questions.append({
        'title': 'title' + str(i),
        'id': i,
        'text': 'text' + str(i),
        'answers_amount': i,
        'publishing_date': '11.09.2001',
        'tags': ['Tag1', 'Tag2', 'Tag3'],
        'likes': 51,
    })

def index(request):
    page = paginate(Question.objects.all(), request, 5)
    return render(request, 'index.html', {
        'page': page,
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': logged_in_user,
    })

answers = []
for i in range(1,4):
    answers.append({
        'id': i,
        'text': 'text' + str(i),
        'is_correct': False,
        'likes': 51,
    })

def question(request, id):
    try:
        return render(request, 'question.html', {
            'question': Question.objects.get(id=id),
            'answers': answers,
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
    page = paginate(questions, request, 5)
    return render(request, 'hot_questions.html', {
        'page': page,
        'page_end_diff': page.paginator.num_pages - page.number,
        'user': logged_in_user,
    })
