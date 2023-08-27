import pytest
from django.conf import settings
from django.urls import reverse
from datetime import timedelta
from news.models import News, Comment
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
def test_news_count(client, news):
    for i in range(11):
        News.objects.create(
            title=f"Заголовок новости {i}",
            text=f"Текст новости {i}")
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.datetime for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, comment, author):
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = timezone.now() + timedelta(days=1)
        comment.save()
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news, author):
    response = client.get(reverse('news:detail', args=[news.id]))
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, news, author):
    client.force_login(author)
    response = client.get(reverse('news:detail', args=[news.id]))
    assert 'form' in response.context
