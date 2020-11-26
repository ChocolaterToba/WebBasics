from django.contrib.auth.models import User
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver

from datetime import datetime, date

class Profile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')

    avatar = models.ImageField(upload_to='avatars/',
                               default='avatars/Toba.jpg',
                               height_field=None, width_field=None,
                               max_length=256, verbose_name='Avatar')
    nickname = models.CharField(max_length = 32, verbose_name='Nickname',
                                default="Default Nickname")

    def __str__(self):
        return self.nickname
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['id']

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user_id=instance.id)
    instance.profile.save()

class QuestionManager(models.Manager):
    def SearchByTag(self, tag):
        return self.filter(tags__name=tag)
    
    def HotWithTag(self, tag):
        return self.SearchByTag(tag).order_by('-rating')
    
    def New(self):
        return self.order_by('-publishing_date')
    
    def Hot(self):
        return self.order_by('-rating')
    
    def Best(self):
        return self.order_by('-rating')


class Question(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    title = models.CharField(max_length=256, verbose_name='Title')
    text = models.TextField(verbose_name='Main text')
    publishing_date = models.DateField(default=date.today, verbose_name='Publishing date')
    rating = models.IntegerField( default=0, verbose_name='Amount of likes')
    tags = models.ManyToManyField('Tag', verbose_name='Tags', blank=True,
                                  related_name="questions", related_query_name="question")
    likes = models.ManyToManyField('Profile', through='QuestionLike', blank=True,
                                   related_name="liked_questions",
                                   related_query_name="liked_question",
                                   verbose_name="Likes")
    objects = QuestionManager()

    def __str__(self):
        return self.title
    
    def LikedOrDislikedBy(self, user):
        try:
            if self.questionlikes.get(user_id=user.id).is_a_like == 1:
                return 'Liked'
            return 'Disliked'
        except QuestionLike.DoesNotExist:
            return 'NoVote'

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
                                         related_query_name="answer")

    text = models.TextField(verbose_name='Main text')
    is_correct = models.BooleanField(default=False, verbose_name='Is answer correct?')
    rating = models.IntegerField(default=0, verbose_name='Amount of likes')
    likes = models.ManyToManyField('Profile', through='AnswerLike', blank=True,
                                   related_name="liked_answers",
                                   related_query_name="liked_answer",
                                   verbose_name="Likes")
    objects = AnswerManager()

    def __str__(self):
        if len(self.text) > 33:
            return self.text[:30] + '...'
        return self.text
    
    def LikedOrDislikedBy(self, user):
        try:
            if self.answerlikes.get(user_id=user.id).is_a_like == 1:
                return 'Liked'
            return 'Disliked'
        except AnswerLike.DoesNotExist:
            return 'NoVote'

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ['id']

class Tag(models.Model):
    name = models.CharField(max_length=32, primary_key=True, verbose_name='Name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

class QuestionLike(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='User that liked')
    question = models.ForeignKey('Question', on_delete=models.CASCADE,
                                 related_name="questionlikes",
                                 verbose_name='Liked question')
    is_a_like = models.IntegerField(default=-1,
                                    choices=(
                                        (-1, 'Dislike'),
                                        (1,  'Like')
                                    ),
                                    verbose_name='Is that a like?')

    def __str__(self):
        return (('Like' if self.is_a_like else 'Dislike') +
                ' by user: ' + self.user.nickname +
                ' on question: ' + self.question.title)

    class Meta:
        verbose_name = 'Like/Dislike on question'
        verbose_name_plural = 'Likes/dislikes on questions'
        ordering = ['id']
        unique_together = ('user_id', 'question_id')

class AnswerLike(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='User that liked')
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE,
                                 related_name="answerlikes",
                                 verbose_name='Liked answer')
    is_a_like = models.IntegerField(default=-1,
                                    choices=(
                                        (-1, 'Dislike'),
                                        (1,  'Like')
                                    ),
                                    verbose_name='Is that a like?')

    def __str__(self):
        return (('Like' if self.is_a_like else 'Dislike')
                + ' on answer: ' + self.answer.text[:10] + '...')

    class Meta:
        verbose_name = 'Like/Dislike on answer'
        verbose_name_plural = 'Likes/dislikes on answers'
        ordering = ['id']
        unique_together = ('user_id', 'answer_id')
