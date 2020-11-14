from django.http import HttpResponse
from django.shortcuts import render

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
for i in range(1,7):
    questions.append({
        'title': 'title' + str(i),
        'id': i,
        'text': 'text' + str(i),
        'answers_amount': i,
        'published_date': '11.09.2001',
        'tags': ['Tag1', 'Tag2', 'Tag3'],
        'likes': 51,
    })

def index(request):
    return render(request, 'index.html', {
        'questions': questions,
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
    return render(request, 'question.html', {
        'question': questions[id - 1],
        'answers': answers,
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
    return render(request, 'tag.html', {
        'questions': questions[:2],
        'tag': tag,
        'user': logged_in_user,
    })

def hot(request):
    return render(request, 'hot_questions.html', {
        'questions': questions[1:4],
        'user': logged_in_user,
    })
