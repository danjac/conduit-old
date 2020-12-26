# Standard Library
import datetime

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

# Conduit
from conduit.articles.models import Article
from conduit.common.turbo import render_turbo_stream_template_to_string
from conduit.common.turbo.response import (
    TurboStreamRemoveResponse,
    TurboStreamTemplateResponse,
)

# Local
from .forms import UserForm


def user_detail(request, username, favorites=False):

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

    if favorites:
        articles = articles.filter(num_likes__gt=0)

    return TemplateResponse(
        request,
        "users/detail.html",
        {
            "user_obj": user,
            "can_follow": can_follow,
            "is_following": is_following,
            "favorites": favorites,
            "articles": articles,
        },
    )


@login_required
def user_settings(request):
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your settings have been saved")
            return redirect(settings.HOME_URL)
        return TurboStreamTemplateResponse(
            request,
            "users/_settings_form.html",
            {"form": form},
            target="settings-form",
            action="update",
        )
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
    return render_follows_response(request, user, is_following=True)


@login_required
@require_POST
def unfollow(request, user_id):
    user = get_object_or_404(request.user.follows.all(), pk=user_id)
    request.user.follows.remove(user)
    return render_follows_response(request, user, is_following=False)


@require_POST
def accept_cookies(request):
    response = TurboStreamRemoveResponse("accept-cookies")
    response.set_cookie(
        "accept-cookies",
        value="true",
        expires=timezone.now() + datetime.timedelta(days=30),
        samesite="Lax",
    )
    return response


def render_follows_response(request, user, is_following):

    context = {"user_obj": user, "is_following": is_following}

    def render():
        for target in [
            "follow-header",
            "follow-body",
        ]:
            yield render_turbo_stream_template_to_string(
                "users/_follow.html",
                context,
                target=target,
                action="update",
                request=request,
            )

    return StreamingHttpResponse(render(), content_type="text/html; turbo-stream;")
