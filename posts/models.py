from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.fields.related import ForeignKey

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL", max_length=50, unique=True)
    description = models.TextField("Описание")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("Текст", help_text="Введите текст поста")
    pub_date = models.DateTimeField("Дата публикации",
                                    auto_now_add=True, db_index=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="author_posts"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="group_posts",
        verbose_name="Группа",
        blank=True,
        null=True,
        help_text="Укажите группу",
    )
    image = models.ImageField(
        "Картинка",
        help_text="Добавьте картинку к посту",
        upload_to="posts/",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField("Текст", help_text="Введите текст коментария")
    created = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        ordering = ["-created"]


class Follow(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE,
                      related_name="follower")
    author = ForeignKey(User, on_delete=models.CASCADE,
                        related_name="following")
