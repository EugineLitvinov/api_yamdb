# Generated by Django 3.2 on 2023-11-22 17:02

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Название категории')),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Комментарий', verbose_name='Текст')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name': ('Комментарий',),
                'verbose_name_plural': 'Комментарии',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Название жанра')),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name': 'Жанр',
                'verbose_name_plural': 'Жанры',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Оценка')),
                ('text', models.TextField(help_text='Отзыв', verbose_name='Текст')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name': ('Отзыв',),
                'verbose_name_plural': 'Отзывы',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название произведения')),
                ('year', models.IntegerField(verbose_name='Год создания')),
                ('rating', models.IntegerField(verbose_name='Рейтинг произведения')),
                ('description', models.TextField(verbose_name='Описание произведения')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='reviews.category', to_field='slug', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Произведение',
                'verbose_name_plural': 'Произведения',
            },
        ),
        migrations.CreateModel(
            name='TitleGenre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reviews.genre')),
                ('title', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reviews.title')),
            ],
        ),
        migrations.AddField(
            model_name='title',
            name='genre',
            field=models.ManyToManyField(through='reviews.TitleGenre', to='reviews.Genre'),
        ),
    ]
