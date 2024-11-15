# Проект Django testing

## Технологический стек
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Pytest](https://img.shields.io/badge/-Pytest-464646?style=flat&logo=Pytest&logoColor=56C0C0&color=008080)](https://docs.pytest.org/en/stable/)
[![Unittest](https://img.shields.io/badge/-Unittest-464646?style=flat&logo=Unittest&logoColor=56C0C0&color=008080)](https://docs.python.org/3/library/unittest.html)

## Краткое описание проекта:
В этом проекте написаны тесты для двух приложений ya_news(pytest) и ya_note(unittest)  
ya_note - сервис для создания заметок  
ya_news - сервис для просмотра новостей
- Тестирование маршрутов
- Тестирование контента
- Тестирование логики приложения

## Запустить проекты:
- Склонируйте репозиторий на свой компьютер:
```git clone git@github.com:valerashankorenko/django_testing.git```
- Если у вас windows\
    `python -m venv venv` -> создать виртуальное окружение\
    `source venv/Scripts/activate` -> активировать виртуальное окружение\
    `python -m pip install --upgrade pip` -> обновить установщик\
    `pip install -r requirements.txt` -> установить зависимости из файла requirements.txt\
    `cd ya_news` или `cd ya_note` -> переходим в папку\
    `python manage.py migrate` -> выполнить миграции\
    `python manage.py loaddata news/fixtures/news.json` -> загрузка данных из файла в БД(только для проекта ya_news)\
    `python manage.py createsuperuser` -> создать суперпользователя\
    `python manage.py runserver` -> запустить проект
- После запуска, проект будет доступен по адресу http://127.0.0.1:8000/
- Панель администратора находиться по адресу http://127.0.0.1:8000/admin/

## Тестировать проекты:
`source venv/Scripts/activate` -> активировать виртуальное окружение\
`cd ya_news` или `cd ya_note` -> переходим в папку\
`pytest` -> Выполнить команду из этой папки(смотря для какого приложения нужно выполнить тесты).

## Тестировать тесты:
`source venv/Scripts/activate` -> активировать виртуальное окружение\
`run_tests.sh` -> Выполнить команду из корня проекта

## Автор проекта:
Валерий Шанкоренко<br/>
Github: [Valera Shankorenko](https://github.com/valerashankorenko)<br/>
Telegram:[@valeron007](https://t.me/valeron007)<br/>
E-mail:valerashankorenko@yandex.by<br/>
