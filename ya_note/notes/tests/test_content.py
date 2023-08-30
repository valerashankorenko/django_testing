from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_note = Note.objects.create(
            title='Заголовок 1',
            text='Текст заметки 1',
            slug='note-slug 1',
            author=cls.reader,
        )

    def test_list_page_contains_single_note(self):
        """Отдельная заметка передаётся на страницу со
        списком заметок в списке object_list в словаре context."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)

        object_list = response.context.get('object_list', [])

        self.assertIn(self.note, object_list)
        self.assertEqual(object_list[0].title, self.note.title)
        self.assertEqual(object_list[0].author, self.note.author)
        self.assertEqual(object_list[0].slug, self.note.slug)

    def test_user_notes_list_contains_own_notes(self):
        """В список заметок одного пользователя не
        попадают заметки другого пользователя."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.note, response.context.get('object_list', []))
        self.assertNotIn(self.reader_note,
                         response.context.get('object_list', []))

    def test_add_note_page_contains_form(self):
        """На страницу создания заметки передаются формы."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, NoteForm)

    def test_edit_note_page_contains_form(self):
        """На страницу редактирования заметки передаются формы."""
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=[self.note.slug])
        response = self.client.get(url)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, NoteForm)
