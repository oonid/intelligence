from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from os import environ
from datetime import datetime, timezone
from requests import get as http_get


def app_people_main(request):
    if "token" not in request.session:  # no token, send auth link
        return HttpResponse('<a href="'+reverse('bc-auth')+'">auth</a>')

    # token exists
    token = request.session["token"]
    # [:-1] to remove 'Z' at the last character in date time str
    token_expires_datetime = datetime.fromisoformat(token["expires_at"][:-1]).astimezone(timezone.utc)

    if token_expires_datetime < datetime.now().astimezone(timezone.utc):  # token expired, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # token still updated
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_user_agent = environ["BASECAMP_USER_AGENT"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    basecamp_api_people_my_profile = f'{basecamp_api_uri}/{basecamp_account_id}/my/profile.json'

    access_token = token["access_token"]

    # request to my profile API
    response = http_get(url=basecamp_api_people_my_profile,
                        headers={"Authorization": "Bearer " + access_token, "User-Agent": basecamp_user_agent})

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    return HttpResponse(
        '<a href="' + reverse('bc-main') + '">back to main</a><br/>'
        f'my profile: {data["name"]} ({data["id"]})<br/>'
        f'<img src="{data["avatar_url"]}" /><br/>')
