from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=get_user_model().objects.create(username="Testname"),
            text="Тестовый текст",
        )

        cls.group = Group.objects.create(
            title="Заголовок",
            description="Описание",
            slug="Slug_test",
        )

    def test_verbose_name(self):
        post = self.post
        field_verboses = {
            "text": "Текст",
            "group": "Группа",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        post = self.post
        field_help_texts = {
            "group": "Укажите группу",
            "text": "Введите текст поста",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_for__str__(self):
        post = self.post
        group = self.group
        expected_object_name_for_post = post.text[:15]
        expected_object_name_for_group = group.title
        self.assertEquals(expected_object_name_for_post, str(post))
        self.assertEquals(expected_object_name_for_group, str(group))
