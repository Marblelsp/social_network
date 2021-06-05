import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.form_comment = CommentForm()

        User = get_user_model()
        cls.user2 = User.objects.create(username="Stas2")
        cls.user = User.objects.create(username="Stas")

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title="Заголовок",
            description="Описание",
            slug="Slug_test",
        )

        cls.post = Post.objects.create(
            author=PostFormTests.user, text="Какой-нибудь текст",
            group=cls.group
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=PostFormTests.user,
            text="Текст тестового комментария",
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_text_label(self):
        text_label = PostFormTests.form.fields["text"].label
        group_label = PostFormTests.form.fields["group"].label
        text_comment_label = PostFormTests.form_comment.fields["text"].label
        self.assertEqual(group_label, "Группа")
        self.assertEqual(text_label, "Текст")
        self.assertEqual(text_comment_label, "Текст")

    def test_text_help_text(self):
        text_help_text = PostFormTests.form.fields["text"].help_text
        gtoup_help_text = PostFormTests.form.fields["group"].help_text
        self.assertEqual(text_help_text, "Введите текст поста")
        self.assertEqual(gtoup_help_text, "Укажите группу")

    def test_create_post(self):
        tasks_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            "text": "Какой-нибудь текст",
            "group": self.group.id,
            'image': uploaded,
        }
        response = PostFormTests.authorized_client.post(
            reverse("new_post"),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertRedirects(response, reverse("index"))
        post = response.context.get("page")[0]
        group = response.context.get("page")[0].group
        self.assertEqual(form_data["text"], post.text)
        self.assertEqual(form_data["group"], group.id)

    def test_edit_post(self):
        self.reverse_post_edit = reverse(
            "post_edit",
            kwargs={
                "username": self.user.username,
                "post_id": self.post.id,
            },
        )
        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            self.reverse_post_edit,
            data=form_data,
            follow=True,
        )
        response_get_page_context = response.context.get("post")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_get_page_context.text, form_data["text"])
        self.assertEqual(response_get_page_context.group, self.group)
        self.assertEqual(response_get_page_context.author, self.user)
        self.assertEqual(Post.objects.count(), post_count)

    def test_comments(self):
        comments_count = Comment.objects.count()
        form_data = {"text": "Текст тестового комментария"}
        response = self.authorized_client.post(
            reverse(
                "add_comment",
                kwargs={
                    "username": self.user.username,
                    "post_id": PostFormTests.post.id,
                },
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(response.status_code, 200)
