import pytest
from datetime import timedelta
from django.utils import timezone

from news.models import News, Comment

NUMBER_OF_NEWS = 11
NUMBER_OF_COMMENTS = 2


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_1(django_user_model):
    return django_user_model.objects.create(username='Автор_1')


@pytest.fixture
def anonymous_client(client):
    return client


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def author_client_1(author_1, client):
    client.force_login(author_1)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        id=1,
        title='Заголовок новости',
        text='Текст новости')
    return news


@pytest.fixture
def news_count():
    for index in range(NUMBER_OF_NEWS):
        News.objects.create(
            title=f"Заголовок новости {index}",
            text=f"Текст новости {index}")


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author)
    return comment


@pytest.fixture
def comments_count(news, comment, author):
    for index in range(NUMBER_OF_COMMENTS):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = timezone.now() + timedelta(days=1)
        comment.save()
