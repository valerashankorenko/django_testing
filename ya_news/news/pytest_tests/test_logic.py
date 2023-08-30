import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus

from news.models import Comment
from news.forms import CommentForm, BAD_WORDS, WARNING

User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cannot_submit_comment(anonymous_client, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=[news.id])
    response = anonymous_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context

    response = anonymous_client.post(url, {'text': 'Текст комментария'})
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_authorized_user_can_submit_comment(author_client, news, author):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=[news.id])
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, CommentForm)

    response = author_client.post(url, {'text': 'Текст комментария'})
    comment = Comment.objects.filter(text='Текст комментария').first()
    assert comment is not None
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=[news.id])
    initial_comments_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors['text'][0] == WARNING
    comments_count = Comment.objects.count()
    assert comments_count == initial_comments_count


@pytest.mark.django_db
def test_authorized_user_can_edit_comment(author_client, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    edit_url = reverse('news:edit', args=[comment.id])
    response = author_client.get(edit_url)
    assert response.status_code == HTTPStatus.OK
    old_text = comment.text
    new_text = 'Измененный текст комментария'
    update_data = {'text': new_text}
    response = author_client.post(edit_url, data=update_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_text
    assert comment.text != old_text


@pytest.mark.django_db
def test_authorized_user_can_delete_comment(author_client, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    delete_url = reverse('news:delete', args=[comment.id])
    response = author_client.get(delete_url)
    assert response.status_code == HTTPStatus.OK
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_authorized_user_cannot_edit_comment_from_another_user(author_client_1,
                                                               comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    initial_content = comment.text
    edit_url = reverse('news:edit', args=[comment.id])
    response = author_client_1.get(edit_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == initial_content


@pytest.mark.django_db
def test_authorized_user_cannot_del_comment_from_another_user(author_client_1,
                                                              comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    initial_count = Comment.objects.count()
    delete_url = reverse('news:delete', args=[comment.id])
    response = author_client_1.get(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count
    assert Comment.objects.filter(id=comment.id).exists()
