from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_pages_availability(self):
        """
        Главная страница доступна анонимному пользователю.
        Страницы регистрации пользователей, входа в учётную запись
        и выхода из неё доступны всем пользователям.
        """
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_authenticated_user(self):
        """
        Аутентифицированному пользователю доступна страница
        со списком заметок notes/, страница успешного добавления заметки done/,
        страница добавления новой заметки add/.
        """
        user = User.objects.create(username='Valera')
        self.client.force_login(user)
        urls = (
            ('notes:add'),
            ('notes:list'),
            ('notes:success'),
        )
        for name in urls:
            with self.subTest(user, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_edit_and_delete(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки
        доступны только автору заметки. Если на эти страницы попытается
        зайти другой пользователь — вернётся ошибка 404.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        При попытке перейти на страницу списка заметок, страницу успешного
        добавления записи, страницу добавления заметки, отдельной заметки,
        редактирования или удаления заметки анонимный пользователь
        перенаправляется на страницу логина.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
