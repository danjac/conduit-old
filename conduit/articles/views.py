# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

# Third Party Libraries
from taggit.models import Tag

# Conduit
from conduit.common.pagination import paginate

# Local
from .forms import ArticleForm, CommentForm
from .models import Article, Comment


def article_index(request):
    """Show list of articles"""

    articles = Article.objects.select_related("author").order_by("-created")
    tags = Tag.objects.all()

    selected_tag = request.GET.get("tag", None)

    if selected_tag:
        articles = articles.filter(tags__name__in=[selected_tag])

    return TemplateResponse(
        request,
        "articles/index.html",
        {
            "articles": paginate(request, articles),
            "tags": tags,
            "selected_tag": selected_tag,
        },
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

    is_following = (
        request.user.is_authenticated
        and article.author.followers.filter(pk=request.user.id).exists()
    )

    can_follow = request.user.is_authenticated and request.user != article.author

    return TemplateResponse(
        request,
        "articles/detail.html",
        {
            "article": article,
            "comment_form": comment_form,
            "comments": paginate(request, comments),
            "is_following": is_following,
            "can_follow": can_follow,
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
