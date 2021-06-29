from django.db import models
from django.forms import ModelForm
from django import forms
from .models import Comment, Group, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["heading", "group", "text", "image", ]

class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ("__all__")
        prepopulated_fields = {"slug": ("title",)}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            'text': forms.Textarea(attrs={'cols': 6, 'rows': 3}),
        }