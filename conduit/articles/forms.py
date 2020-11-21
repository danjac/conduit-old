from django import forms


from .models import Article, Comment


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("slug", "title", "description", "body")
        labels = {
            "title": "Article Title",
            "description": "What's this article about?",
            "slug": "Article URL",
            "body": "Write your article (in Markdown)",
        }
        widgets = {"description": forms.TextInput()}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        labels = {"body": "Write a comment..."}
