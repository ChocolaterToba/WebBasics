from django.contrib.auth.models import User
from django.db import models

from datetime import datetime, date

class Profile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)

    avatar = models.ImageField(upload_to='avatars/',
                               height_field=None, width_field=None,
                               max_length=256, verbose_name='Avatar')
    nickname = models.CharField(max_length = 32, verbose_name='Nickname')

    def LikedOrDisliked(self, post):
        if isinstance(post, Question):
            result_query = self.liked_questions.filter(id=post.id)
        elif isinstance(post, Answer):
            result_query = self.liked_answers.filter(id=post.id)
        else:
            return 'NoVote'

        if result_query.exists():
            if isinstance(result_query[0], Question):
                if (result_query.filter(questionlike__is_a_like=True).exists()):
                    return 'Liked'
            elif (result_query.filter(answerlike__is_a_like=True).exists()):
                return 'Liked'
            return 'Disliked'

        return 'NoVote'   

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
        return self.order_by('-rating')
    
    def Best(self):
        return self.order_by('-rating')


class Question(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    title = models.CharField(max_length=256, verbose_name='Title')
    text = models.TextField(verbose_name='Main text')
    publishing_date = models.DateField(default=date.today, verbose_name='Publishing date')
    rating = models.IntegerField(verbose_name='Amount of likes', default=0)
    tags = models.ManyToManyField('Tag', verbose_name='Tags', blank=True,
                                  related_name="questions", related_query_name="question")
    likes = models.ManyToManyField('Profile', through='QuestionLike',
                                   verbose_name="Likes", blank=True,
                                   related_name="liked_questions",
                                   related_query_name="liked_question")
    objects = QuestionManager()

    def RefreshRating(self):
        self.rating = QuestionLike.objects.GetRating(self.id)
        self.save()  # Otherwise, new rating will be erased.

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
                                         related_query_name="answer")

    text = models.TextField(verbose_name='Main text')
    is_correct = models.BooleanField(verbose_name='Is answer correct?', default=False)
    rating = models.IntegerField(verbose_name='Amount of likes', default=0)
    likes = models.ManyToManyField('Profile', through='AnswerLike',
                                   verbose_name="Likes", blank=True,
                                   related_name="liked_answers",
                                   related_query_name="liked_answer")
    objects = AnswerManager()

    def RefreshRating(self):
        self.rating = AnswerLike.objects.GetRating(self.id)
        self.save()  # Otherwise, new rating will be erased.

    def __str__(self):
        return self.text[:30] + '...'

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

class QuestionLikeManager(models.Manager):
    def GetRating(self, question_id):
        related_likes = self.filter(question_id=question_id)
        return related_likes.filter(is_a_like=True).count() - related_likes.filter(is_a_like=False).count()

class QuestionLike(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    is_a_like = models.BooleanField(verbose_name='Is that a like?')
    objects = QuestionLikeManager()

    def __str__(self):
        return (('Like' if self.is_a_like else 'Dislike')
               + ' on question: ' + self.question.title)

    class Meta:
        verbose_name = 'Like/Dislike on question'
        verbose_name_plural = 'Likes/dislikes on questions'
        ordering = ['id']

class AnswerLikeManager(models.Manager):
    def GetRating(self, answer_id):
        related_likes = self.filter(answer_id=answer_id)
        return related_likes.filter(is_a_like=True).count() - related_likes.filter(is_a_like=False).count()

class AnswerLike(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)
    is_a_like = models.BooleanField(verbose_name='Is that a like?')
    objects = AnswerLikeManager()

    def __str__(self):
        return (('Like' if self.is_a_like else 'Dislike')
                + ' on answer: ' + self.answer.text[:10] + '...')

    class Meta:
        verbose_name = 'Like/Dislike on answer'
        verbose_name_plural = 'Likes/dislikes on answers'
        ordering = ['id']
