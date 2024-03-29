# Django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

# Third Party Libraries
import pytest

# Conduit
from conduit.articles.factories import ArticleFactory, CommentFactory
from conduit.users.factories import UserFactory


@pytest.fixture
def get_response():
    return lambda req: HttpResponse()


@pytest.fixture
def user_model():
    return get_user_model()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
def login_user(client):
    password = "testpass1"
    user = UserFactory()
    user.set_password(password)
    user.save()
    client.login(username=user.username, password=password)
    return user


@pytest.fixture
def article(user):
    return ArticleFactory(author=user)


@pytest.fixture
def comment(article, user):
    return CommentFactory(article=article, author=user)
