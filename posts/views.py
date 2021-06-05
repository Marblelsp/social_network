from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator, 'post_list': post_list}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'group': group, 'page': page,
               'paginator': paginator, 'posts': posts}
    return render(request, 'group.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.author_posts.all()
    post_count = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    followers_count = author.following.count()
    follows_count = author.follower.count()
    following = (
        request.user.is_authenticated and
        author.following.filter(user=request.user, author=author).exists()
    )
    context = {
        'page': page,
        'profile': author,
        'followers_count': followers_count,
        'follows_count': follows_count,
        'post_count': post_count,
        'post_list': post_list,
        'following': following,
        'paginator': paginator,
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    post_list = post.author.author_posts.all()
    post_count = post_list.count()
    comments = post.comments.all()
    form = CommentForm()
    followers_count = post.author.following.count()
    follows_count = post.author.follower.count()
    context = {
        'author': post.author,
        'post': post,
        'profile': post.author,
        'post_count': post_count,
        'comments': comments,
        'followers_count': followers_count,
        'follows_count': follows_count,
        'form': form,
    }
    return render(request, 'posts/post.html', context)


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'posts/post_edit.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/post_edit.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('post', username=request.user.username,
                        post_id=post_id)
    return render(
        request, 'posts/post_edit.html', {'form': form, 'post': post,
                                          'is_edit': True}
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if request.GET or not form.is_valid():
        return redirect('post', username=username, post_id=post_id)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.select_related('group').filter(
        author__following__user=request.user
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/follow.html', {'page': page,
                                                 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(request, 'misc/404.html',
                  {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
