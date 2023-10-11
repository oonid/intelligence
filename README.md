# djbc: django basecamp

A brief exploration of a web app built with [Django](https://www.djangoproject.com/), which interacts with the [Basecamp API](https://github.com/basecamp/bc3-api).

## Development

Instead of manually running the Django web server with `manage.py runserver`, I have created a `docker-compose.yml` file.
This allows you to easily run the project with the following command:

```bash
docker-compose up
```

The `docker-compose` command will build the `basecamp_app` using the `docker build` process,
with configurations defined in the `Dockerfile`.

If you need to access `django-admin` or `manage.py` commands, make sure to navigate to the `basecamp_app` directory
before using them.

To add a new Django app named `bc`, use the `django-admin` command:
```shell
cd basecamp_app
django-admin startapp bc
```
To apply model changes, utilize the `manage.py` script:
```shell
cd basecamp_app
python manage.py migrate
```

### Structure

The Django project is located inside the `basecamp_app` directory and is named `djbc`.

I have placed the virtual environment within the `basecamp_app` directory, specifically in the `venv` subdirectory.
The packages that need to be installed using `pip` are listed in the `requirements.txt` file.
You can easily install them by running the following command from within your virtual environment:

```bash
pip install -r requirements.txt
```

### Packages

* `Django`: A web framework designed for perfectionists with deadlines.
* `djangorestframework`: Used to build APIs on top of Django.
* `gunicorn`: A Python web server (WSGI) often paired with nginx.
* `requests`: An HTTP client used to facilitate the OAuth process.

### Files

Sample of `.env.dev`:
```
DEBUG=1
SECRET_KEY="s*cret"
DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1 [::1]"
DJANGO_ALLOW_ASYNC_UNSAFE="true"
```
