# Django
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

# Conduit
from conduit.articles.models import Article
from conduit.common.pagination import paginate


def user_detail(request, username):

    user = get_object_or_404(get_user_model(), username=username)

    is_following = (
        request.user.is_authenticated
        and user.followers.filter(pk=request.user.id).exists()
    )

    can_follow = request.user.is_authenticated and request.user != user

    articles = (
        Article.objects.filter(author=user)
        .select_related("author")
        .order_by("-created")
    )

    return TemplateResponse(
        request,
        "users/detail.html",
        {
            "user_obj": user,
            "can_follow": can_follow,
            "is_following": is_following,
            "articles": paginate(request, articles),
        },
    )


@login_required
@require_POST
def follow(request, pk):
    user = get_object_or_404(
        get_user_model().objects.exclude(pk=request.user.id), pk=pk
    )
    request.user.follows.add(user)
    messages.success(request, f"You are now following {user}")
    return redirect(user)


@login_required
@require_POST
def unfollow(request, pk):
    user = get_object_or_404(request.user.follows.all(), pk=pk)
    request.user.follows.remove(user)
    messages.info(request, f"You have stopped following {user}")
    return redirect(user)
