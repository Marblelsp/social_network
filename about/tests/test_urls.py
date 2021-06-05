from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create(username='Stas')

        cls.post = Post.objects.create(
            author=StaticURLTests.user,
            text='Тестовый текст',
        )

    def setUp(self):
        super().setUp()
        self.guest_client = Client()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
