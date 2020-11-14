from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)

    avatar = models.ImageField(upload_to='uploads/avatars/',
                               height_field=None, width_field=None,
                               max_length=256, verbose_name='Avatar')
    nickname = models.CharField(max_length = 32, verbose_name='Nickname')
    email = models.EmailField(max_length = 256, verbose_name='E-mail')

    def __str__(self):
        return self.nickname
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

class Question(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    title = models.CharField(max_length=256, verbose_name='Title')
    text = models.TextField(verbose_name='Main text')
    publishing_date = models.DateField(auto_now_add=True, verbose_name='Publishing date')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

class Answer(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    related_question = models.ForeignKey('Question', on_delete=models.CASCADE)

    text = models.TextField(verbose_name='Main text')
    is_correct = models.BooleanField(verbose_name='Is answer correct?')
    likes_amount = models.IntegerField(verbose_name='Amount of likes')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'

class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='Name')
    related_questions = models.ManyToManyField('Question', verbose_name='Related questions')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

class QuestionLike(models.Model):
    user = models.OneToOneField('Profile', on_delete=models.CASCADE)
    question = models.OneToOneField('Question', on_delete=models.CASCADE)
    is_a_like = models.BooleanField(verbose_name='Is that a like?')

    def __str__(self):
        return 'Question Like'

    class Meta:
        verbose_name = 'Like on question'
        verbose_name_plural = 'Likes on questions'

class AnswerLike(models.Model):
    user = models.OneToOneField('Profile', on_delete=models.CASCADE)
    answer = models.OneToOneField('Answer', on_delete=models.CASCADE)
    is_a_like = models.BooleanField(verbose_name='Is that a like?')

    def __str__(self):
        return 'Answer Like'

    class Meta:
        verbose_name = 'Like on answer'
        verbose_name_plural = 'Likes on answers'
