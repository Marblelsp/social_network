from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create(username="Stas")
        cls.user2 = User.objects.create(username="Boris")

        cls.group = Group.objects.create(
            title="Заголовок",
            description="Описание",
            slug="Slug_test",
        )

        cls.group2 = Group.objects.create(
            title="Заголовок2",
            description="Описание2",
            slug="Slug_test2",
        )

        cls.post = Post.objects.create(
            author=cls.user, text="Тестовый текст", group=cls.group
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text="Какой-нибудь текст комента",
        )

        Post.objects.bulk_create(
            [
                Post(author=cls.user2, text=f"Тестовый текст + {i}")
                for i in list(range(10))
            ]
        )
        cls.follow = Follow.objects.create(user=cls.user, author=cls.user2)

    def setUp(self):
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            "posts/index.html": reverse("index"),
            "posts/post_edit.html": reverse(
                "post_edit",
                kwargs={
                    "username": self.user.username,
                    "post_id": self.post.id,
                },
            ),
            "group.html": reverse("group", kwargs={"slug": "Slug_test"}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_show_correct_context_index(self):
        response = self.authorized_client.get(reverse("new_post"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("index"))
        context = response.context.get("page").object_list
        self.assertListEqual(list(context), list(Post.objects.all()[:10]))

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("group", kwargs={"slug": "Slug_test"})
        )
        actual_group = response.context.get("group")
        actual_posts = response.context.get("posts")[0]
        self.assertEqual(self.group, actual_group)
        self.assertEqual(self.post, actual_posts)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("profile", kwargs={"username": "Stas"})
        )
        context = response.context.get("post_list")[0]
        self.assertEqual(context, self.post)

    def test_post_view_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("post", args=[self.user, self.post.id])
        )
        response_auth = self.authorized_client.get(
            reverse("post", args=[self.comment.author, self.comment.post.id])
        )
        actual_post = response.context.get("post")
        self.assertEqual(self.post, actual_post)
        self.assertEqual(Post.objects.count(), 11)
        self.assertEqual(response_auth.context["comments"][0].author,
                         self.comment.author)
        self.assertEqual(response_auth.context["comments"][0].post,
                         self.comment.post)
        self.assertEqual(response_auth.context["comments"][0].text,
                         self.comment.text)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                "post_edit",
                kwargs={"username": "Stas", "post_id": self.post.id}
            )
        )
        actual_post = response.context.get("post")
        self.assertEqual(self.post, actual_post)

    def test_post_with_group_appears_in_index(self):
        post_new = Post.objects.create(
            author=self.user, text="Тестовый текст_new", group=self.group
        )
        response = self.authorized_client.get(reverse("index"))
        posts = response.context.get("post_list")[0]
        self.assertEqual(post_new, posts)

    def test_post_with_group_appears_in_group_slug(self):
        post_new = Post.objects.create(
            author=self.user, text="Тестовый текст_new", group=self.group
        )
        response = self.authorized_client.get(
            reverse("group", kwargs={"slug": "Slug_test"})
        )
        posts = response.context.get("posts")[0]
        self.assertEqual(post_new, posts)

    def test_post_with_group_appears_in_other_group(self):
        post_new = Post.objects.create(
            author=self.user, text="Тестовый текст_new", group=self.group2
        )
        response = self.authorized_client.get(
            reverse("group", kwargs={"slug": "Slug_test"})
        )
        posts = response.context.get("posts")[:10]
        self.assertNotIn(post_new, posts)

    def test_authorized_client_follow(self):
        self.authorized_client.post(
            reverse("profile_follow", kwargs={"username": self.user2})
        )
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.user2).exists()
        )

    def test_authorized_client_unfollow(self):
        self.authorized_client.post(
            reverse("profile_unfollow", kwargs={"username": self.user2})
        )
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.user2).exists()
        )

    def test_post_index_for_follower(self):
        test_post = Post.objects.create(
            author=self.user2,
            text="Тестовый текст для подписчика",
            group=self.group
        )
        response = self.authorized_client.get(reverse("follow_index"))
        post_for_follower = response.context.get("page").object_list
        self.assertIn(test_post, post_for_follower)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create(username="Mihail")

        Post.objects.bulk_create(
            [Post(author=cls.user, text="Тестовый текст") for i in range(13)]
        )

    def test_first_page_containse_ten_records(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.client.get(reverse("index") + "?page=2")
        self.assertEqual(len(response.context.get("page").object_list), 3)
