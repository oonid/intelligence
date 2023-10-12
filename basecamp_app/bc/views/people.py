from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import Template, RequestContext
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
    if "identity" not in request.session:  # no identity, strip token and redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # identity exists
    identity = request.session["identity"]

    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_user_agent = environ["BASECAMP_USER_AGENT"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    basecamp_api_people_my_profile = f'{basecamp_api_uri}/{basecamp_account_id}/my/profile.json'

    access_token = token["access_token"]

    # request to people my profile API
    response = http_get(url=basecamp_api_people_my_profile,
                        headers={"Authorization": "Bearer " + access_token, "User-Agent": basecamp_user_agent})

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    identity["id"] = data["id"]  # overwrite the user ID
    request.session["identity"] = identity

    return HttpResponse(
        '<a href="' + reverse('bc-main') + '">back to main</a><br/>'
        '<a href="' + reverse('app-people-person') + '">people get person</a><br/>'
        f'my profile: {data["name"]} ({data["id"]})<br/>'
        f'<img src="{data["avatar_url"]}" /><br/>')


def app_people_person(request):
    if "token" not in request.session:  # no token, send auth link
        return HttpResponse('<a href="'+reverse('bc-auth')+'">auth</a>')

    # token exists
    token = request.session["token"]
    # [:-1] to remove 'Z' at the last character in date time str
    token_expires_datetime = datetime.fromisoformat(token["expires_at"][:-1]).astimezone(timezone.utc)

    if token_expires_datetime < datetime.now().astimezone(timezone.utc):  # token expired, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # token still updated
    if "identity" not in request.session:  # no identity, strip token and redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # identity exists
    identity = request.session["identity"]

    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_user_agent = environ["BASECAMP_USER_AGENT"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization

    access_token = token["access_token"]

    people_id = identity["id"] if identity["id"] > 0 else 0
    data = None
    basecamp_api_people_get_person = ''

    if request.method == 'POST':
        people_id = request.POST.get("people_id")
        basecamp_api_people_get_person = f'{basecamp_api_uri}/{basecamp_account_id}/people/{people_id}.json'

        # request to people get person API
        response = http_get(url=basecamp_api_people_get_person,
                            headers={"Authorization": "Bearer " + access_token, "User-Agent": basecamp_user_agent})

        if response.status_code != 200:  # not OK
            return HttpResponse('', status=response.status_code)

        # if OK
        data = response.json()

    # all methods (GET, POST, etc.)

    t = Template(
            '<a href="' + reverse('app-people-main') + '">back to main</a><br/>'
            '<form action="' + reverse('app-people-person') + '" method="post">'
            '{% csrf_token %}'
            '<label for="people_id">People ID: </label>'
            '<input id="people_id" type="text" name="people_id" value="{{ people_id }}" required>'
            '<input type="submit" value="Submit">'
            '</form><br/>'
            '{{ api_people_get_person }}<br/>'
            '{{ people_profile }}<br/>'
            '{% if people_avatar_url %}<img src="{{ people_avatar_url }}" />{% endif %}<br/>')

    c = RequestContext(request,
                       {'api_people_get_person': basecamp_api_people_get_person,
                        'people_id': people_id,
                        'people_profile': f'profile: {data["name"]} ({data["id"]})' if data else '',
                        'people_avatar_url': f'{data["avatar_url"]}' if data else ''})

    return HttpResponse(t.render(c))
