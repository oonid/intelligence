from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from os import environ
from datetime import datetime, timezone
from requests import get as http_get, post as http_post


def basecamp_main(request):
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

    return HttpResponse(
        f'hello, {identity["first_name"]} {identity["last_name"]}<br/>'
        f'your <a href="#'+token["access_token"]+'">token</a>.<br/>'
        '<ul>'
        '<li><a href="'+reverse('app-people-main')+'">people</a></li>'
        '<li><a href="'+reverse('app-project-main')+'">project</a></li>'
        '</ul>')


def basecamp_auth(request):
    """
    docs reference:
    * https://github.com/basecamp/api/blob/master/sections/authentication.md

    :param request:
    :return:
    """
    try:
        del request.session["token"]  # entering auth URI manually will flush the saved session
    except KeyError:
        pass
    try:
        del request.session["identity"]  # entering auth URI manually will flush the saved session
    except KeyError:
        pass

    basecamp_client_id = environ["BASECAMP_CLIENT_ID"]
    basecamp_redirect_uri = environ["BASECAMP_REDIRECT_URI"]
    return HttpResponseRedirect(
        'https://launchpad.37signals.com/authorization/new?type=web_server&'
        f'client_id={basecamp_client_id}&redirect_uri={basecamp_redirect_uri}'
    )


def basecamp_redirect(request):
    if 'code' not in request.GET:
        return HttpResponse('', status=400)  # response with bad request

    response_code = request.GET.get('code')
    basecamp_token_uri = 'https://launchpad.37signals.com/authorization/token'
    basecamp_authorization_uri = 'https://launchpad.37signals.com/authorization.json'
    basecamp_client_id = environ["BASECAMP_CLIENT_ID"]
    basecamp_client_secret = environ["BASECAMP_CLIENT_SECRET"]
    basecamp_redirect_uri = environ["BASECAMP_REDIRECT_URI"]
    basecamp_user_agent = environ["BASECAMP_USER_AGENT"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization

    # request token to basecamp token URI
    response = http_post(url=basecamp_token_uri,
                         data={"type": "web_server",
                               "client_id": basecamp_client_id,
                               "client_secret": basecamp_client_secret,
                               "redirect_uri": basecamp_redirect_uri,
                               "code": response_code})

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    access_token = data['access_token']
    refresh_token = data['refresh_token']

    # request authorization details to basecamp authorization URI
    response = http_get(url=basecamp_authorization_uri,
                        headers={"Authorization": "Bearer " + access_token, "User-Agent": basecamp_user_agent})

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    token_expires_at = data['expires_at']
    basecamp_identity = data['identity']
    basecamp_accounts = data['accounts']
    basecamp_account = basecamp_accounts[0]  # just pick the first account

    # overwrite account if predefined account ID exists
    for account in basecamp_accounts:
        if account["id"] == basecamp_account_id:
            basecamp_account = account

    request.session["token"] = {
        "expires_at": token_expires_at,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    # as mentioned on docs: The id field should NOT be used for submitting data
    # https://github.com/basecamp/api/blob/master/sections/authentication.md
    request.session["identity"] = {
        "id": 0,
        "email_address": basecamp_identity["email_address"],
        "first_name": basecamp_identity["first_name"],
        "last_name": basecamp_identity["last_name"],
        "bc_id": basecamp_account["id"],
        "bc_name": basecamp_account["name"],
        "bc_href": basecamp_account["href"],
    }

    return HttpResponseRedirect(reverse('bc-main'))
