from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import time
from itertools import islice, chain
from math import ceil

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

BATCH_SIZE = 100000  #  Batch size for bulk_create

class Command(BaseCommand):
    help = 'Filling database'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--users', type=int, help='Usernames amount')
        parser.add_argument('-q', '--questions', type=int, help='Questions amount')
        parser.add_argument('-a', '--answers', type=int, help='Answers amount')
        parser.add_argument('-t', '--tags', type=int, help='Tags amount')
        parser.add_argument('-l', '--likes', type=int, help='Total likes amount')
        parser.add_argument('-s', '--db_size', type=str, help='Preset amounts')
        
    
    def handle(self, *args, **kwargs):
        users_cnt = kwargs['users']
        questions_cnt = kwargs['questions']
        answers_cnt = kwargs['answers']
        tags_cnt = kwargs['tags']
        likes_cnt = kwargs['likes']
        db_size = kwargs['db_size']
        
        if db_size:
            if db_size == 'small':
                users_cnt = 20
                questions_cnt = 30
                answers_cnt = 60
                tags_cnt = 10
                likes_cnt = 1000
            elif db_size == 'medium':
                users_cnt = 1000
                questions_cnt = 5000
                answers_cnt = 10000
                tags_cnt = 500
                likes_cnt = 100000
            elif db_size == 'large':
                users_cnt =  10000
                questions_cnt = 100000
                answers_cnt = 1000000
                tags_cnt = 10000
                likes_cnt = 2000000

        if users_cnt:
            print('Generating users...')
            self.fill_profiles(users_cnt)
            print('Users generated')
        base_user, created = User.objects.get_or_create(
            username='basic',
            defaults={
                'username': 'basic',
                'email': 'Example@mail.ru',
                'password': 'thisismyhair'
            }
        )
        base_profile, created = Profile.objects.get_or_create(
            user_id=base_user.id,
            defaults={
                'user_id': base_user.id,
                'avatar': 'avatars/image1.jpg',
                'nickname': 'basicNick'
            }
        )
        
        if tags_cnt:
            print('Generating tags...')
            self.fill_tags(tags_cnt)
            print('Tags generated')

        if questions_cnt:
            print('Generating questions...')
            self.fill_questions(questions_cnt)
            print('Questions generated')
        
        if answers_cnt:
            print('Generating answers...')
            self.fill_answers(answers_cnt)
            print('Answers generated')
        
        if likes_cnt:
            print('Generating likes...')
            start_time = time.time()
            self.fill_likes(likes_cnt)
            print('Likes generated, time: {}s'.format(time.time() - start_time))
            
            print('Refreshing ratings')
            with transaction.atomic():
                for question in Question.objects.all():
                    question.rating = sum(question.questionlikes.values_list('is_a_like', flat=True))
                    question.save()
                
                for answer in Answer.objects.all():
                    answer.rating = sum(answer.answerlikes.values_list('is_a_like', flat=True))
                    answer.save()
            print('Ratings refreshed')

    def fill_users(self, cnt):
        users_generator = (User(
            username=f.unique.name(),
            email=f.unique.email(),
            password=f.password(length=f.random_int(min=8, max=12))
            ) for i in range(cnt))

        self.bulk_create_in_batches(cnt, users_generator, User)
        
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

        profiles_generator = (Profile(
            user_id=user_ids[i],
            avatar='avatars/' + choice(avatar_links),
            nickname=f.first_name()[:31]
            ) for i in range(cnt))

        self.bulk_create_in_batches(cnt, profiles_generator, Profile)

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

        questions_generator = (Question(
            author_id=choice(profile_ids),
            title=f.sentence(nb_words=5)[:256],
            text='. '.join(f.sentences(f.random_int(min=2, max=7))),
            publishing_date=f.date_between('-40y', 'today')
            ) for i in range(cnt))
        
        self.bulk_create_in_batches(cnt, questions_generator, Question)
    
    def fill_answers(self, cnt):
        profile_ids = list(
            Profile.objects.values_list(
                'id', flat=True
            )
        )
        
        question_ids = list(
            Question.objects.values_list(
                'id', flat=True
            )
        )

        answers_generator = (Answer(
            author_id=choice(profile_ids),
            related_question_id = choice(question_ids),
            text='. '.join(f.sentences(f.random_int(min=2, max=10))),
            is_correct = f.pybool()
            ) for i in range(cnt))
        
        self.bulk_create_in_batches(cnt, answers_generator, Answer)
    
    def fill_likes(self, cnt):
        profile_ids = list(
            Profile.objects.values_list(
                'id', flat=True
            )
        )

        question_ids = list(
            Question.objects.values_list(
                'id', flat=True
            )
        )

        answer_ids = list(
            Answer.objects.values_list(
                'id', flat=True
            )
        )

        question_likes_amount = int(cnt / 2)
        answer_likes_amount = cnt - question_likes_amount

        question_likes_generator = (QuestionLike(
            user_id=choice(profile_ids),
            question_id=choice(question_ids),
            is_a_like=choice((1, -1))
            ) for i in range(question_likes_amount))

        self.bulk_create_in_batches(cnt, question_likes_generator, QuestionLike, True)

        answer_likes_generator = (AnswerLike(
            user_id=choice(profile_ids),
            answer_id=choice(answer_ids),
            is_a_like=choice((1, -1))
            ) for i in range(answer_likes_amount))

        self.bulk_create_in_batches(cnt, answer_likes_generator, AnswerLike, True)
    
    def fill_tags(self, cnt):
        tags_generator = (Tag(
            name='Tag' + str(f.unique.random_int(min=0, max=100000))
            ) for i in range(cnt))
        
        self.bulk_create_in_batches(cnt, tags_generator, Tag)
    
    def bulk_create_in_batches(self, cnt, generator, model_type, ignore_conflicts=False):
        if cnt > BATCH_SIZE:
            batch_amount = ceil(cnt / BATCH_SIZE)
            print('\n' + str(batch_amount) + '\n')
            for i in range(batch_amount):
                print(i)
                batch = islice(generator, BATCH_SIZE)
                model_type.objects.bulk_create(batch, BATCH_SIZE,
                                               ignore_conflicts=ignore_conflicts)
        else:
            model_type.objects.bulk_create(generator,
                                           ignore_conflicts=ignore_conflicts)
