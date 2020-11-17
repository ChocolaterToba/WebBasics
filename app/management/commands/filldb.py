from django.core.management.base import BaseCommand, CommandError

import time

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
Faker.seed(1234)

QUESTION_LIKES_DENOMINATOR = 5 # 1/Q... of users max like certain post.

ANSWER_LIKES_DENOMINATOR = 10

ANSWER_MAX_AMOUNT = 3 # Maximum amount of answers per question.

class Command(BaseCommand):
    help = 'Filling database'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--users', type=int, help='Usernames amount')
        parser.add_argument('-q', '--questions', type=int, help='Questions amount')
        parser.add_argument('-t', '--tags', type=int, help='Tags amount')
        parser.add_argument('-s', '--db_size', type=str, help='Preset amounts')
        
    
    def handle(self, *args, **kwargs):
        users_cnt = kwargs['users']
        questions_cnt = kwargs['questions']
        tags_cnt = kwargs['tags']
        db_size = kwargs['db_size']
        
        if db_size:
            if db_size == 'small':
                users_cnt = 20
                questions_cnt = 30
                tags_cnt = 10
            elif db_size == 'medium':
                users_cnt = 100
                questions_cnt = 5000
                tags_cnt = 500
            elif db_size == 'large':
                users_cnt =  10000
                questions_cnt = 100000
                tags_cnt = 10000

        if users_cnt:
            print('Generating users...')
            self.fill_profiles(users_cnt)
            print('Users generated')
        
        if tags_cnt:
            print('Generating tags...')
            self.fill_tags(tags_cnt)
            print('Tags generated')

        if questions_cnt:
            print('Generating questions...')
            self.fill_questions(questions_cnt)
            print('Questions generated')

    def fill_users(self, cnt):
        users_generator = (User(
            username=f.unique.last_name()[:20],
            email=f.unique.email(),
            password=f.password(length=f.random_int(min=8, max=12))
            ) for i in range(cnt))
        User.objects.bulk_create(users_generator)
        
    def fill_profiles(self, cnt):
        initial_users_amount = User.objects.count()
        self.fill_users(cnt)
        user_ids = sorted(list(
            User.objects.values_list(
                'id', flat=True
            )
        ))[initial_users_amount:]

        avatars_path = 'uploads/avatars/'
        avatar_links = [f for f in listdir(avatars_path) if isfile(join(avatars_path, f))]
        for i in range(cnt):
            Profile.objects.create(
                user_id=user_ids[i],
                avatar='avatars/' + choice(avatar_links),
                nickname=f.first_name()[:31]
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
            question = Question.objects.create(
                author_id=choice(profile_ids),
                title=f.sentence(nb_words=5)[:256],
                text='. '.join(f.sentences(f.random_int(min=2, max=7))),
                publishing_date=f.date_between('-40y', 'today'),
            )

            # Setting tags.
            question.tags.set(choices(tag_names, k=f.random_int(min=0, max=min(5, Tag.objects.count()))))
            
            # Setting likes.
            question.likes.set(choices(profile_ids, k=f.random_int(min=0, max=int(len(profile_ids) /
                                                                                  QUESTION_LIKES_DENOMINATOR))),
                               through_defaults={'is_a_like': 1})
            
            # Setting dislikes (set() will override some of the likes).
            question.likes.add(*choices(profile_ids, k=f.random_int(min=0, max=int(len(profile_ids) /
                                                                                   QUESTION_LIKES_DENOMINATOR))),
                               through_defaults={'is_a_like': -1})

            question.rating = sum(question.questionlikes.values_list('is_a_like', flat=True))
            question.save()
            self.fill_answers(question, f.random_int(min=0, max=ANSWER_MAX_AMOUNT))
    
    def fill_answers(self, question, cnt):
        profile_ids = list(
            Profile.objects.values_list(
                'id', flat=True
            )
        )
        profile_ids.remove(question.author_id)

        for i in range(cnt):
            answer = Answer.objects.create(
                author_id=choice(profile_ids),
                related_question_id = question.id,
                text='. '.join(f.sentences(f.random_int(min=2, max=7))),
                is_correct = f.pybool()
                )


            # Setting likes.
            answer.likes.set(choices(profile_ids, k=f.random_int(min=0, max=int(len(profile_ids) /
                                                                                ANSWER_LIKES_DENOMINATOR))),
                             through_defaults={'is_a_like': 1})
            
            # Setting dislikes (set() will override some of the likes).
            answer.likes.add(*choices(profile_ids, k=f.random_int(min=0, max=int(len(profile_ids) /
                                                                                 ANSWER_LIKES_DENOMINATOR))),
                             through_defaults={'is_a_like': -1})
            answer.rating = sum(answer.answerlikes.values_list('is_a_like', flat=True))
            answer.save()
    
    def fill_tags(self, cnt):
        for i in range(cnt):
            Tag.objects.create(name=f.unique.word())
