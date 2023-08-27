import pytest
from django.urls import reverse
from news.models import Comment
from news.forms import BAD_WORDS, WARNING
from http import HTTPStatus


@pytest.mark.django_db
def test_anonymous_user_cannot_submit_comment(anonymous_client, news):
    url = reverse('news:detail', args=[news.id])
    response = anonymous_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context

    response = anonymous_client.post(url, {'text': 'Текст комментария'})
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_authorized_user_can_submit_comment(author_client, news):
    url = reverse('news:detail', args=[news.id])
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context

    response = author_client.post(url, {'text': 'Текст комментария'})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(text='Текст комментария').exists()


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=[news.id])
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors['text'][0] == WARNING

    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_authorized_user_can_edit_comment(author_client, comment):
    edit_url = reverse('news:edit', args=[comment.id])
    response = author_client.get(edit_url)
    assert response.status_code == HTTPStatus.OK

    new_text = 'Измененный текст комментария'
    update_data = {'text': new_text}
    response = author_client.post(edit_url, data=update_data)
    assert response.status_code == HTTPStatus.FOUND

    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_authorized_user_can_delete_comment(author_client, comment):
    delete_url = reverse('news:delete', args=[comment.id])
    response = author_client.get(delete_url)
    assert response.status_code == HTTPStatus.OK

    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND

    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_authorized_user_cannot_edit_comment_from_another_user(author_client_1,
                                                               comment):
    edit_url = reverse('news:edit', args=[comment.id])
    response = author_client_1.get(edit_url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_authorized_user_cannot_del_comment_from_another_user(author_client_1,
                                                              comment):
    delete_url = reverse('news:delete', args=[comment.id])
    response = author_client_1.get(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
