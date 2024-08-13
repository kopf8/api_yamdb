# 📝 [api_yamdb](https://github.com/kopf8/api_yamdb.git)
<br><hr>

### Contents:

1. [Project tech stack](#project-tech-stack)
2. [Description](#project-description)
3. [User access levels](#user-access-levels)
4. [Install & run the project](#install-and-run-the-project)
5. [Project created by](#project-created-by)
<br><hr>

## Project tech stack:
- [Python 3.9](https://www.python.org/)
- [Django 3.2.16](https://www.djangoproject.com/)
- [Django REST Framework 3.2.14](https://www.django-rest-framework.org/)
- [Simple JWT 4.7.2](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)

<br><hr>
## Project description:

The YaMDb project collects user reviews of books, movies and music.
The reviewed items themselves are not stored in YaMDb, you cannot watch a movie or listen to music here.

<br><hr>
## User access levels:

Any user can view descriptions of works, read reviews and comments.

### Authorized user can:

Add reviews, comments and give ratings. This user can leave only one review per item.

### Unauthorized user can:

View descriptions of items, read reviews and comments.

### Admin can:

Add works, categories, genres, reviews, comments and give ratings.

<br><hr>

## Install and run the project:

Clone repository and switch to project directory using command line:

```
git clone https://github.com/kopf8/api_yamdb.git
```

```
cd api_yamdb
```

Create & activate virtual environment:

```
python -m venv .venv
```

* For Linux/macOS:

    ```
    source .venv/bin/activate
    ```

* For Win:

    ```
    source .venv/Scripts/activate
    ```

Upgrade pip:

```
python -m pip install --upgrade pip
```

Install project requirements from file _requirements.txt_:

```
pip install -r requirements.txt
```

Make & run migrations:

```
python manage.py makemigrations
python manage.py migrate
```

Launch server from directory _**api_yamdb/api_yamdb**_:

```
python manage.py runserver
```
<br><hr>

## Necessary links available after server is launched:
Project itself: `http://127.0.0.1:8000`

Admin panel: `http://127.0.0.1:8000/admin` 

Project documentation: `http://127.0.0.1:8000/redoc/`

<br><hr>
## Project created by:
[Maria Kirsanova](https://github.com/kopf8) as team lead

Created models, viewsets & endpoints for

* titles
* categories
* genres;

Created import of CSV data into the database.

[Tatyana Zakharova](https://github.com/tvzakharova)

Wrote the whole part about user management:

* registration and authentication system
* access rights
* work with the token
* confirmation via e-mail.

[Nickolay Privezentsev](https://github.com/nprivezentsev)

Created everything for:

* reviews,
* comments,
* ratings.
