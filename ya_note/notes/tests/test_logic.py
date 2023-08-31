from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify as translit_slugify
from http import HTTPStatus

from notes.models import Note

User = get_user_model()


class NoteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note_slug',
            author=cls.author,
        )

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный  пользователь не может создать заметку."""
        url = reverse('notes:add')
        initial_notes_count = Note.objects.count()
        response = self.client.post(url)
        final_notes_count = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + url)
        self.assertEqual(initial_notes_count, final_notes_count)

    def test_logged_in_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        initial_note_count = Note.objects.count()
        self.client.force_login(self.author)
        url = reverse('notes:add')
        data = {'title': 'Заголовок',
                'text': 'Текст заметки',
                'slug': 'Slug'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_note_count + 1)

        note = Note.objects.last()
        self.assertEqual(note.title, data['title'])
        self.assertEqual(note.text, data['text'])
        self.assertEqual(note.author, self.author)

    def test_duplicate_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.client.force_login(self.author)
        initial_note_count = Note.objects.count()
        url = reverse('notes:add')
        data = {'title': 'Заголовок 2',
                'text': 'Текст заметки 2',
                'slug': 'note_slug'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        final_note_count = Note.objects.count()
        self.assertEqual(final_note_count, initial_note_count)

    def test_create_note_without_a_slug(self):
        """Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify."""
        self.client.force_login(self.author)
        data = {
            'title': 'Заголовок 3',
            'text': 'Текст заметки'
        }
        response = self.client.post(reverse('notes:add'), data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        created_note = Note.objects.get(title=data['title'])
        expected_slug = translit_slugify(data['title'])
        self.assertEqual(created_note.slug, expected_slug)

    def test_logged_in_user_can_edit_note(self):
        """Залогиненный пользователь может редактировать свою заметку."""
        self.client.force_login(self.author)
        new_content = "Новое содержимое заметки"
        response = self.client.post('notes:edit',
                                    args=(self.note.slug,),
                                    data={'text': new_content})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertNotEqual(updated_note.text, new_content)
        self.assertEqual(updated_note.author, self.author)

    def test_logged_in_user_can_edit_own_note(self):
        """Залогиненный пользователь не может редактировать чужую заметку."""
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        data = {'text': 'Новый текст'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.title, self.note.title)
        self.assertEqual(updated_note.slug, self.note.slug)

    def test_logged_in_user_can_delete_note(self):
        """Залогиненный пользователь может удалить свою заметку."""
        self.client.force_login(self.author)
        response = self.client.delete(reverse('notes:delete',
                                              args=(self.note.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(slug=self.note.slug).exists())

    def test_logged_in_user_can_delete_own_note(self):
        """Залогиненный пользователь не может удалить чужую заметку."""
        another_user = User.objects.create_user(username='another_user',
                                                password='testpassword')
        another_users_note = Note.objects.create(text='Текст заметки',
                                                 author=another_user)
        initial_count = Note.objects.count()
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(another_users_note.slug,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        final_count = Note.objects.count()
        self.assertEqual(final_count, initial_count)

    def test_test_anonymous_user_cannot_edit_note(self):
        """Анонимный  пользователь не может редактировать заметку."""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = reverse('users:login') + '?next=' + url
        self.assertRedirects(response, expected_url)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Заголовок")
        self.assertEqual(self.note.text, "Текст заметки")
        self.assertEqual(self.note.author, self.author)

    def test_test_anonymous_user_cannot_delete_note(self):
        """Анонимный  пользователь не может удалять заметку."""
        url = reverse('notes:delete', args=(self.note.slug,))
        num_notes_before = Note.objects.count()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_redirect_url = reverse('users:login') + '?next=' + url
        self.assertRedirects(response, expected_redirect_url)
        note_exists = Note.objects.filter(slug=self.note.slug).exists()
        self.assertTrue(note_exists)
        num_notes_after = Note.objects.count()
        self.assertEqual(num_notes_before, num_notes_after)
