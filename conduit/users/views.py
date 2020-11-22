# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

# Conduit
from conduit.articles.models import Article
from conduit.common.pagination import paginate

# Local
from .forms import UserForm


def user_detail(request, username):

    user = get_object_or_404(get_user_model(), username=username)

    is_following = (
        request.user.is_authenticated
        and user.followers.filter(pk=request.user.id).exists()
    )

    can_follow = request.user.is_authenticated and request.user != user

    articles = (
        Article.objects.filter(author=user)
        .with_num_likes()
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
def user_settings(request):
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(settings.HOME_URL)
    else:
        form = UserForm(instance=request.user)
    return TemplateResponse(request, "users/settings.html", {"form": form})


@login_required
@require_POST
def follow(request, user_id):
    user = get_object_or_404(
        get_user_model().objects.exclude(pk=request.user.id), pk=user_id
    )
    request.user.follows.add(user)
    messages.success(request, f"You are now following {user}")
    return redirect(user)


@login_required
@require_POST
def unfollow(request, user_id):
    user = get_object_or_404(request.user.follows.all(), pk=user_id)
    request.user.follows.remove(user)
    messages.info(request, f"You have stopped following {user}")
    return redirect(user)
