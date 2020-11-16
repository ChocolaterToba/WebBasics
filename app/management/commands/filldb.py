from django.core.management.base import BaseCommand, CommandError

# App models
from django.contrib.auth.models import User
from app.models import Profile, Question, Answer, Tag
from app.models import QuestionLike, AnswerLike

# File usils to get all image paths
from os import listdir
from os.path import isfile, join
from django.core.files import File

from faker import Faker
from random import choice, choices

f = Faker(['en-US', 'ru_RU'])


class Command(BaseCommand):
    help = 'Filling database'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--users', type=int, help='Usernames amount')
        parser.add_argument('-q', '--questions', type=int, help='Questions amount')
        parser.add_argument('-a', '--answers', type=int, help='Answers amount')
    
    def handle(self, *args, **kwargs):
        users_cnt = kwargs['users']
        questions_cnt = kwargs['questions']
        answers_cnt = kwargs['answers']

        if users_cnt:
            print('====================')
            self.fill_users(users_cnt)
            print('------------------------')
            self.fill_profiles(users_cnt)
            print('++++++++++++++++++++++++')
            if questions_cnt:
               self.fill_questions(questions_cnt)

    def fill_users(self, cnt):
        for i in range(cnt):
            User.objects.create_user(
                f.first_name(),
                f.email(),
                f.password(length=f.random_int(min=8, max=12)))
        
    def fill_profiles(self, cnt):
        user_ids = list(
            User.objects.values_list(
                'id', flat=True
            )
        )

        avatars_path = 'uploads/avatars/'
        avatar_links = [f for f in listdir(avatars_path) if isfile(join(avatars_path, f))]
        for i in range(cnt):
            Profile.objects.create(
                user=user_ids[i],
                avatar='avatars/' + choice(avatar_links),
                nickname=f.name()[:31]
            )

    def fill_questions(self, cnt):
        profile_ids = list(
            Profile.objects.values_list(
                'id', flat=True
            )
        )
        tag_names = list(
            Tag.objects.values_list(
                'name', flat=True
            )
        )
        for i in range(cnt):
            Question.objects.create(
                author=choice(profile_ids),
                title=f.sentence(nb_words=5)[:256],
                text='. '.join(f.sentences(f.random_int(min=2, max=7))),
                publishing_date=f.date_between('1970.01.01', 'today'),
                tags=choices(tag_names, k=f.random_int(min=0, max=5)),
                likes=choices(profile_ids, k=f.random_int(min=0, max=len(profile_ids)))
            )
            Question.objects.last().RefreshRating()
