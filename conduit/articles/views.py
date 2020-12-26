# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

# Third Party Libraries
from taggit.models import TaggedItem

# Conduit
from conduit.common.turbo import render_turbo_stream
from conduit.common.turbo.response import (
    TurboStreamRemoveResponse,
    TurboStreamTemplateResponse,
)

# Local
from .forms import ArticleForm, CommentForm
from .models import Article, Comment


def article_index(request, follows=False, tag=None):
    """Show list of articles"""

    articles = (
        Article.objects.with_num_likes().select_related("author").order_by("-created")
    )

    tags = (
        TaggedItem.objects.select_related("tag")
        .values_list("tag__slug", "tag__name")
        .distinct()
    )

    if tag:
        articles = articles.filter(tags__slug__in=[tag])

    if follows and request.user.is_authenticated:
        articles = articles.filter(author__in=request.user.follows.all())

    return TemplateResponse(
        request,
        "articles/index.html",
        {"articles": articles, "tags": tags, "follows": follows, "tag": tag,},
    )


def article_detail(request, slug):

    article = get_object_or_404(
        Article.objects.with_num_likes().select_related("author"), slug=slug,
    )

    comment_form = None

    if request.user.is_authenticated:
        if request.method == "POST":
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.author = request.user
                comment.article = article
                comment.save()
                messages.success(request, "Your comment has been posted")
            return redirect(article)
        else:
            comment_form = CommentForm()

    comments = article.comment_set.select_related("author").order_by("-created")

    is_following = (
        request.user.is_authenticated
        and article.author.followers.filter(pk=request.user.id).exists()
    )

    can_follow = can_like = (
        request.user.is_authenticated and request.user != article.author
    )

    can_edit = request.user.is_authenticated and request.user == article.author

    return TemplateResponse(
        request,
        "articles/detail.html",
        {
            "article": article,
            "comment_form": comment_form,
            "comments": comments,
            "is_following": is_following,
            "can_follow": can_follow,
            "can_like": can_like,
            "can_edit": can_edit,
        },
    )


@login_required
def create_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            # save tags
            form.save_m2m()
            messages.success(request, "Your article has been published!")
            return redirect("articles:index")
        return TurboStreamTemplateResponse(
            request,
            "articles/_article_form.html",
            {"form": form},
            target="article-form",
            action="update",
        )
    else:
        form = ArticleForm()
    return TemplateResponse(request, "articles/article_form.html", {"form": form})


@login_required
def edit_article(request, article_id):
    article = get_object_or_404(Article, author=request.user, pk=article_id)
    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, "Your article has been updated")
            return redirect(article)
        return TurboStreamTemplateResponse(
            request,
            "articles/_article_form.html",
            {"form": form},
            target="article-form",
            action="update",
        )
    else:
        form = ArticleForm(instance=article)
    return TemplateResponse(
        request, "articles/article_form.html", {"form": form, "article": article}
    )


@login_required
@require_POST
def like_article(request, article_id):
    article = get_object_or_404(
        Article.objects.exclude(author=request.user), pk=article_id
    )

    if request.user.likes.filter(pk=article_id).exists():
        request.user.likes.remove(article)
    else:
        request.user.likes.add(article)

    num_likes = article.likers.count()

    def render_likes():

        for target in [
            f"article-likes-{article.id}",
            "article-likes-header",
            "article-likes-body",
        ]:
            yield render_turbo_stream(target=target, action="update", content=num_likes)

    return StreamingHttpResponse(
        render_likes(), content_type="text/html; turbo-stream;"
    )


@login_required
@require_POST
def delete_article(request, article_id):
    article = get_object_or_404(Article, author=request.user, pk=article_id)
    article.delete()
    messages.info(request, "Your article has been deleted")
    return redirect("articles:index")


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related("article", "author"),
        author=request.user,
        pk=comment_id,
    )
    comment.delete()
    return TurboStreamRemoveResponse(f"comment-{comment_id}")
