from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify
from notes.models import Note

User = get_user_model()


class NoteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')

        cls.note_slug = slugify('Уникальный Slug')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=cls.note_slug,
            author=cls.author,
        )

        cls.reader_note_slug = slugify('Другой Slug')
        cls.reader_note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=cls.reader_note_slug,
            author=cls.reader,
        )

    def test_anonymous_user_cannot_create_note(self):
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:login') + '?next=' + url)

    def test_logged_in_user_can_create_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_duplicate_slug_error_handling(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_can_edit_own_note(self):
        self.client.force_login(self.author)
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_edit_others_note(self):
        self.client.force_login(self.author)
        edit_url = reverse('notes:edit', args=(self.reader_note.slug,))
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 404)

    def test_user_can_delete_own_note(self):
        self.client.force_login(self.author)
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_delete_others_note(self):
        self.client.force_login(self.author)
        delete_url = reverse('notes:delete', args=(self.reader_note.slug,))
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 404)
