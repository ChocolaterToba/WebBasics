# Generated by Django 3.1.3 on 2020-11-14 22:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Main text')),
                ('is_correct', models.BooleanField(verbose_name='Is answer correct?')),
                ('likes_amount', models.IntegerField(verbose_name='Amount of likes')),
            ],
            options={
                'verbose_name': 'Asnwer',
                'verbose_name_plural': 'Answers',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(max_length=256, upload_to='uploads/avatars/', verbose_name='Avatar')),
                ('nickname', models.CharField(max_length=32, verbose_name='Nickname')),
                ('email', models.EmailField(max_length=256, verbose_name='E-mail')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('text', models.TextField(verbose_name='Main text')),
                ('publishing_date', models.DateField(auto_now_add=True, verbose_name='Publishing date')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.profile')),
            ],
            options={
                'verbose_name': 'Question',
                'verbose_name_plural': 'Questions',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('related_questions', models.ManyToManyField(to='app.Question', verbose_name='Related questions')),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='QuestionLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_a_like', models.BooleanField(verbose_name='Is that a like?')),
                ('question', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.question')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.profile')),
            ],
            options={
                'verbose_name': 'Like on question',
                'verbose_name_plural': 'Likes on questions',
            },
        ),
        migrations.CreateModel(
            name='AnswerLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_a_like', models.BooleanField(verbose_name='Is that a like?')),
                ('answer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.answer')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.profile')),
            ],
            options={
                'verbose_name': 'Like on answer',
                'verbose_name_plural': 'Likes on answers',
            },
        ),
        migrations.AddField(
            model_name='answer',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.profile'),
        ),
        migrations.AddField(
            model_name='answer',
            name='related_question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.question'),
        ),
    ]
