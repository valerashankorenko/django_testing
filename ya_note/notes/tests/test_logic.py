from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify
from pytils import translit
from http import HTTPStatus

from notes.models import Note

User = get_user_model()


class NoteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')

        cls.note_slug = slugify('Slug')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=cls.note_slug,
            author=cls.author,
        )

        cls.reader_note_slug = slugify('Slug1')
        cls.reader_note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=cls.reader_note_slug,
            author=cls.reader,
        )

    def setUp(self):
        Note.objects.all().delete()

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный  пользователь не может создать заметку."""
        url = reverse('notes:add')
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + url)

    def test_logged_in_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        data = {'title': 'Заголовок',
                'text': 'Текст заметки',
                'slug': 'Slug'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.get()
        self.assertEqual(note.title, 'Заголовок')
        self.assertEqual(note.text, 'Текст заметки')
        self.assertEqual(note.author, self.author)

    def test_duplicate_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = {'title': 'Заголовок 2',
                'text': 'Текст заметки 2',
                'slug': self.note_slug}
        response = self.client.post(url, data)
        note_data = {'title': 'Заголовок 1',
                     'text': 'Текст заметки 1',
                     'slug': 'Slug'}
        response = self.client.post(url, note_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_note_without_a_slug(self):
        """Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify."""
        note_content = self.note
        note = Note()
        note.content = note_content
        note.slug = translit.slugify(note_content)
        self.assertTrue(note)
        expected_slug = translit.slugify(note_content)
        self.assertEqual(note.slug, expected_slug)

    def logged_in_user_can_edit_note(self):
        """Залогиненный пользователь может редактировать свою заметку."""
        self.client.force_login(self.author)
        response = self.client.post('notes:edit', args=(self.note.slug,))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.content, self.note)
        self.assertEqual(updated_note.author, self.author)

    def logged_in_user_can_edit_own_note(self):
        """Залогиненный пользователь не может редактировать чужую заметку."""
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        data = {'text': 'Новый текст'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.content, 'Текст заметки')

    def logged_in_user_can_delete_note(self):
        """Залогиненный пользователь может удалить свою заметку."""
        self.client.force_login(self.author)
        response = self.client.delete('notes:delete', args=(self.note.slug,))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.content, self.note)
        self.assertEqual(updated_note.author, self.author)

    def logged_in_user_can_delete_own_note(self):
        """Залогиненный пользователь не может удалить чужую заметку."""
        self.client.force_login(self.author)
        url = reverse('notes:', args=(self.note.slug,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.content, 'Текст заметки')

    def test_anonymous_user_cannot_edit_note(self):
        """Анонимный  пользователь не может редактировать заметку."""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + url)

    def test_anonymous_user_cannot_delete_note(self):
        """Анонимный  пользователь не может удалять заметку."""
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + url)
