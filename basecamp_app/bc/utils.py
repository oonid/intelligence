from datetime import datetime, timezone
from os import environ
from requests import get as http_get

# utilities to process environment variables, sessions, and APIs


def bc_api_get(uri, access_token):
    basecamp_user_agent = environ["BASECAMP_USER_AGENT"]
    return http_get(url=uri,
                    headers={"Authorization": "Bearer " + access_token, "User-Agent": basecamp_user_agent})


def api_people_my_profile_uri():
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/my/profile.json'


def api_people_get_person_uri(people_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/people/{people_id}.json'


def api_project_get_all_projects_uri():
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/projects.json'


def api_project_get_project_uri(project_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/projects/{project_id}.json'


def session_get_token_and_identity(request):
    """

    :param request:
    :return: tuple of dicts: token, identity
    """
    token = None
    identity = None

    if "token" not in request.session:  # no token in session, return None
        return token, identity  # None

    # token exists
    token = request.session["token"]
    # [:-1] to remove 'Z' at the last character in date time str
    token_expires_datetime = datetime.fromisoformat(token["expires_at"][:-1]).astimezone(timezone.utc)

    if token_expires_datetime < datetime.now().astimezone(timezone.utc):  # token expired, strip token, return None
        try:
            del request.session["token"]
        except KeyError:
            pass

        return token, identity  # None

    # token still updated
    if "identity" not in request.session:  # no identity, strip token and return None
        try:
            del request.session["token"]
        except KeyError:
            pass

        return token, identity  # None

    # identity exists
    identity = request.session["identity"]

    # return token and identity
    return token, identity