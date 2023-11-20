from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=256,
                            unique=True,
                            blank=False,
                            verbose_name='Название категории')
    slug = models.SlugField(max_length=50,
                            unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    # TODO найти нужные миксины
    name = models.CharField(max_length=256,
                            unique=True,
                            blank=False,
                            verbose_name='Название жанра')
    slug = models.SlugField(max_length=50,
                            unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(max_length=256,
                            verbose_name='Название произведения',
                            blank=False)
    # TODO - написать валидатор по времени(не больше текущего года)
    year = models.IntegerField(blank=False,
                               verbose_name='Год создания')
    # Будет заполняться отдельной функцией
    rating = models.IntegerField(verbose_name='Рейтинг произведения')
    description = models.TextField(verbose_name='Описание произведения')
    genre = models.ManyToManyField(Genre, through='TitleGenre')
    category = models.ForeignKey(Category,
                                 to_field='slug',
                                 on_delete=models.SET_NULL,
                                 blank=False,
                                 null=True,
                                 verbose_name='Категория',)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class TitleGenre(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.title}{self.genre}'
