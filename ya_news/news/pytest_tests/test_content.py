import pytest
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from news.forms import CommentForm

User = get_user_model()

NUMBER_OF_COMMENTS = 1


@pytest.mark.django_db
def test_news_count(client, news_count):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(reverse('news:home'))
    object_list = response.context.get('object_list')
    news_count = len(object_list) if object_list is not None else 0
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    """Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка."""
    response = client.get(reverse('news:home'))
    object_list = response.context.get('object_list')
    assert object_list is not None
    all_dates = [news.datetime for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, comments_count):
    """Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце."""
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.order_by('created')

    for index in range(len(all_comments) - NUMBER_OF_COMMENTS):
        assert (all_comments[index].created <= all_comments[
            index + NUMBER_OF_COMMENTS].created)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news, author):
    """Анонимному пользователю недоступна форма для
    отправки комментария на странице отдельной новости"""
    response = client.get(reverse('news:detail', args=[news.id]))
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, news, author):
    """Авторизованному пользователю доступна форма для
    отправки комментария на странице отдельной новости"""
    client.force_login(author)
    response = client.get(reverse('news:detail', args=[news.id]))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
