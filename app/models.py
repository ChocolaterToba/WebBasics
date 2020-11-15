from django.contrib.auth.models import User
from django.db import models

from datetime import datetime

class Profile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)

    avatar = models.ImageField(upload_to='avatars/',
                               height_field=None, width_field=None,
                               max_length=256, verbose_name='Avatar')
    nickname = models.CharField(max_length = 32, verbose_name='Nickname')

    def __str__(self):
        return self.nickname
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['id']

class QuestionManager(models.Manager):
    def SearchByTag(self, tag):
        return self.filter(tags__name=tag)
    
    def New(self):
        return self.order_by('-publishing_date')
    
    def Hot(self):
        # Hot questions are today's questions with best ratings.
        return self.filter(publishing_date=datetime.today()).order_by('-rating')
    
    def Best(self):
        return self.order_by('-rating')


class Question(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE,)
    title = models.CharField(max_length=256, verbose_name='Title')
    text = models.TextField(verbose_name='Main text')
    publishing_date = models.DateField(auto_now_add=True, verbose_name='Publishing date')
    rating = models.IntegerField(verbose_name='Amount of likes')
    tags = models.ManyToManyField('Tag', verbose_name='Tags', blank=True,
                                  related_name="questions", related_query_name="question",)
    likes = models.ManyToManyField('Profile', through='QuestionLike',
                                   verbose_name="Likes", blank=True,
                                   related_name="liked_questions",
                                   related_query_name="liked_question",)
    objects = QuestionManager()

    def RefreshRating(self):
        self.rating = self.likes.objects.GetRating()
    
    def AnswersAmount(self):
        return self.answers.count()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['id']

class AnswerManager(models.Manager):
    def Best(self):
        return self.order_by('-rating')

class Answer(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    related_question = models.ForeignKey('Question', on_delete=models.CASCADE,
                                         related_name="answers",
                                         related_query_name="answer",)

    text = models.TextField(verbose_name='Main text')
    is_correct = models.BooleanField(verbose_name='Is answer correct?')
    rating = models.IntegerField(verbose_name='Amount of likes')
    likes = models.ManyToManyField('Profile', through='AnswerLike',
                                   verbose_name="Likes", blank=True,
                                   related_name="liked_answers",
                                   related_query_name="liked_answer",)
    objects = AnswerManager()

    def RefreshRating(self):
        self.rating = self.likes.objects.GetRating()
    


    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ['id']

class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='Name', primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

class LikeManager(models.Manager):
    def GetRating(self):
        return self.objects.count() - self.filter(is_a_like=True).count()

class QuestionLike(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    is_a_like = models.BooleanField(verbose_name='Is that a like?')
    objects = LikeManager()

    def __str__(self):
        return 'Question Like'

    class Meta:
        verbose_name = 'Like on question'
        verbose_name_plural = 'Likes on questions'
        ordering = ['id']

class AnswerLike(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)
    is_a_like = models.BooleanField(verbose_name='Is that a like?')
    objects = LikeManager()

    def __str__(self):
        return 'Answer Like'

    class Meta:
        verbose_name = 'Like on answer'
        verbose_name_plural = 'Likes on answers'
        ordering = ['id']
