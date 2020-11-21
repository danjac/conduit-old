# Django
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

# Conduit
from conduit.articles.models import Article
from conduit.common.pagination import paginate


def user_detail(request, username):

    author = get_object_or_404(get_user_model(), username=username)

    is_following = (
        request.user.is_authenticated
        and author.followers.filter(pk=request.user.id).exists()
    )

    can_follow = request.user.is_authenticated and request.user != author

    articles = (
        Article.objects.filter(author=author)
        .select_related("author")
        .order_by("-created")
    )

    return TemplateResponse(
        request,
        "users/detail.html",
        {
            "articles": paginate(request, articles),
            "user_obj": author,
            "can_follow": can_follow,
            "is_following": is_following,
        },
    )


@login_required
def follow(request, pk):
    user = get_object_or_404(
        get_user_model().objects.exclude(pk=request.user.id), pk=pk
    )
    request.user.follows.add(user)
    messages.success(request, f"You are now following {user}")
    return redirect(user)


@login_required
def unfollow(request, pk):
    user = get_object_or_404(request.user.follows.all(), pk=pk)
    request.user.follows.remove(user)
    messages.info(request, f"You have stopped following {user}")
    return redirect(user)
