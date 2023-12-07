# intelligence

A brief exploration of a web app built with [Django](https://www.djangoproject.com/) that interacts with the [Basecamp API](https://github.com/basecamp/bc3-api).

Objectives:
* Implement OAuth to allow users to log in easily and obtain an access token, which is then saved in cookie-based sessions.
* Create a form input for user input in API calls.
* Implement webhooks.

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

The Django project is located inside the `basecamp_app` directory and is named `intelligence`.

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
* `coverage`: A tool used for measuring code coverage, assessing the effectiveness of tests.

### Files

Sample of `.env.dev`:
```
DEBUG=1
SECRET_KEY="s*cret"
DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1 [::1]"
DJANGO_ALLOW_ASYNC_UNSAFE="true"
```

### Settings

#### Sessions

The session engine in settings.py has been changed from the default database-backed to 
[cookie-based](https://docs.djangoproject.com/en/dev/topics/http/sessions/#using-cookie-based-sessions) sessions.
We opted for the cookie-based approach as it is more convenient during the early development phase when the database 
might not be in use yet.

#### Cache

Even though it is not explicitly mentioned in settings.py, we have chosen to utilize the default cache setting,
employing a [local-memory cache](https://docs.djangoproject.com/en/dev/topics/cache/#local-memory-caching) backend. 
We will use the cache as the transfer medium for tokens between the web app and API, as we only need it temporarily 
(and, in many cases, it is not recommended).
