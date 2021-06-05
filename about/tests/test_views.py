from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post


class StaticViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create(username='Stas')

        cls.group = Group.objects.create(
            title='Заголовок',
            description='Описание',
            slug='Slug_test',
        )
        cls.post = Post.objects.create(
            author=StaticViewsTests.user,
            text='Тестовый текст',
            group=StaticViewsTests.group
        )

        cls.form = PostForm()

    def setUp(self):
        super().setUp()
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
