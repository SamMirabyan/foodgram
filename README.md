
![yamdb_final workflow](https://github.com/sammirabyan/foodgram-project-react/actions/workflows/foodgram_backend_workflow.yml/badge.svg)


<div style="text-align: center">

# Веб сервис Foodgram

</div>

<div style="text-align: justify">

[![N|Solid](https://images.pexels.com/photos/3338497/pexels-photo-3338497.jpeg)](https://github.com/SamMirabyan/foodgram-project-react)

## Задумали приготовить что-то вкусненькое? Доверьтесь Foodgram!


### С Foodgram вы можете
- создавать и редактировать свои рецепты;
- просматривать рецепты других авторов и добавлять их в избранное или в корзину покупок;
- просматривать профили интересных вам авторов и подписываться на них;
- выгрузить содержимое корзины в пдф файл и отправиться за покупками с уверенностью, что ничего не забудете.

### Технические требования и зависимости

Для того, чтобы развернуть проект вам понадобятся установленные **docker** и **docker-compose**.
Остальные зависимости будут установлены из файлов docker:whale:.

### Как запустить
1. Склонируйте данный репозиторий.
2. Скопируйте на локальную машину или удаленный сервер следующие файлы и директории:
    - файл ```docker-compose.yml```;
    - директории ```docs/``` и ```docker/```;
3. Создайте файл ```.env``` в одной директории с файлом ```docker-compose.yml``` и укажите в нем необходимые переменные.
4. Запустите контейнеры
    ```
    docker-compose up -d --build
    ```
5. Залейте тестовые данные в базу
    ```
    docker-compose exec python manage.py loadtestdata
    ```
6. **Важно!** В случае удаления тестовых данных с помощью, например ```python manage.py flush``` будут полностью удалены предустановленные данные типов ингредиентов. Во избежание неожиданного поведения БД рекомендуется полностью удалить volume базы данных и вновь собрать контнейры.
7. **Важно**: обязательно измените workflow-инструкции файла `.github/workflows/foodgram_backend_workflow.yml` под нужды своего проекта. 

### Архитектура сервиса
Сервис собран в 3-х docker контейнерах, управляемых с помощью docker-compose:
- Nginx :mailbox_with_no_mail:: сервер статики и прокси сервер для бэкэнда;
- front:dress:: React приложение, скомпилированное с помощью npm run build. Раздается nginx'ом;
- backend :electric_plug:: Django Rest Framework :gun: + Gunicorn :carousel_horse:;
- database :1234:: postgres (дефолтный image для docker).

### Интересные задачи, решенные в процессе работы над сервисом
- создание и редактирование связанных моделей через глубоко вложенные сериализаторы:
    - например сериализатор создания рецепта использует сериализатор ингредиента, который использует сериализатор типа ингредиента...
- использование кастомных management комманд для заливки тестовых данных в базу;
- использование миграций для заливки всех типов ингредиентов при создании БД;
- использование сигналов для удаления связанной с рецептом картинки после удаления рецепта;
- использование кастомных фильтров и пагинаторов для корректного отображения рецептов в бразуере;
- преобразование html шаблона в пдф документ и его скачивание;
- использование системы аутентификации с помощью токенов и использование кастомных пермишенов.

### Над чем еще нужно поработать
- добавить тесты;
- включить тестирование в этапы workflow.

### Над проектом работали
- frontend и спеки в redoc предоставлены [Yandex Prakticum Team](https://github.com/yandex-praktikum);
- backend и docker:whale:'ная часть написаны [Sam Mirabyan](https://sammirabyan.github.io).

### Обложка
[pexels.com](https://www.pexels.com/ru-ru/photo/3338497/)

</div>