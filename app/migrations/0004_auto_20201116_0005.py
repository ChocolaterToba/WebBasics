# Generated by Django 3.1.3 on 2020-11-16 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20201115_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='rating',
            field=models.IntegerField(default=0, verbose_name='Amount of likes'),
        ),
        migrations.AlterField(
            model_name='question',
            name='rating',
            field=models.IntegerField(default=0, verbose_name='Amount of likes'),
        ),
    ]
