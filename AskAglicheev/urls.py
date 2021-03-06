"""Ask Aglicheev URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('settings/', views.settings, name='settings'),
    path('tag/<str:tag>/', views.tag, name='tag'),
    path('hot/', views.hot, name='hot'),
    path('logout/', views.logout, name='logout'),
    path('vote/', views.vote, name='vote'),
    path('mark_correct/', views.mark_correct, name='mark_correct'),
    path('hello_world/', views.hello_world, name='hello_world'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
