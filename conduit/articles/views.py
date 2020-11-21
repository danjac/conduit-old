# Django
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

# Conduit
from conduit.common.pagination import paginate

# Local
from .forms import ArticleForm, CommentForm
from .models import Article, Comment


def article_index(request):
    """Show list of articles"""

    articles = Article.objects.select_related("author").order_by("-created")

    return TemplateResponse(
        request, "articles/index.html", {"articles": paginate(request, articles)}
    )


def article_author_index(request, username):

    author = get_object_or_404(get_user_model(), username=username)

    articles = (
        Article.objects.filter(author=author)
        .select_related("author")
        .order_by("-created")
    )

    return TemplateResponse(
        request,
        "articles/author.html",
        {"articles": paginate(request, articles), "author": author},
    )


def article_detail(request, slug):

    article = get_object_or_404(Article.objects.select_related("author"), slug=slug)

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

    return TemplateResponse(
        request,
        "articles/detail.html",
        {
            "article": article,
            "comment_form": comment_form,
            "comments": paginate(request, comments),
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
            messages.success(request, "Your article has been published!")
            return redirect("articles:index")
    else:
        form = ArticleForm()
    return TemplateResponse(request, "articles/article_form.html", {"form": form})


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related("article", "author"),
        author=request.user,
        pk=comment_id,
    )
    comment.delete()
    messages.info(request, "Your comment has been deleted")
    return redirect(comment.article)
