from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create(username="Stas")
        cls.user2 = User.objects.create(username="Ivan")

        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
        )

        cls.group = Group.objects.create(
            title="Заголовок",
            description="Описание",
            slug="Slug_test",
        )

    def setUp(self):
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)

    def test_urls_uses_correct_template_for_authorized_client(self):
        templates_url_names = {
            'posts/index.html': '/',
            'posts/post_edit.html': '/new/',
            'group.html': '/group/Slug_test/',
            'posts/profile.html': '/Stas/',
            'posts/post.html': '/Stas/1/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_for_guest_client(self):
        templates_url_names = {
            "posts/index.html": "/",
            "group.html": "/group/Slug_test/",
            "posts/profile.html": "/Stas/",
            "posts/post.html": "/Stas/1/",
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_for_guest_client(self):
        response = self.guest_client.get("/Stas/1/edit/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/auth/login/?next=/Stas/1/edit/")

    def test_status_code_for_authorized_client(self):
        url_names = ["/", "/group/Slug_test/", "/new/",
                     "/Stas/1/", "/Stas/1/edit/"]
        for url in url_names:
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_status_code_for_guest_client(self):
        url_names = ["/new/", "/Stas/1/edit/"]
        for url in url_names:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, 302)

    def test_status_code_for_anouther_client(self):
        response = self.authorized_client2.get('/Stas/1/edit/')
        self.assertEqual(response.status_code, 302)
