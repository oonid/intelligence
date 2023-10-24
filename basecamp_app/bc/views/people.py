from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import Template, RequestContext

from bc.serializers import BcPeopleSerializer
from bc.utils import (session_get_token_and_identity, bc_api_get, api_people_my_profile_uri, api_people_get_person_uri,
                      api_people_get_all_people_uri)


def app_people_main(request):

    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to people my profile API
    response = bc_api_get(uri=api_people_my_profile_uri(), access_token=token["access_token"])

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

    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    people_id = identity["id"] if identity["id"] > 0 else 0
    data = None
    api_people_get_person = ''  # init, will be updated on form post

    if request.method == 'POST':
        try:
            people_id = int(request.POST.get("people_id"))
            if people_id <= 0:  # invalid
                return HttpResponse('', status=400)

        except ValueError:
            return HttpResponse('', status=400)

        # request to people get person API
        api_people_get_person = api_people_get_person_uri(people_id=people_id)
        response = bc_api_get(uri=api_people_get_person, access_token=token["access_token"])

        if response.status_code != 200:  # not OK
            return HttpResponse('', status=response.status_code)

        # if OK
        data = response.json()

    # all methods (GET, POST, etc.)

    t = Template(
            '<a href="' + reverse('app-people-main') + '">back</a><br/>'
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
                       {'api_people_get_person': api_people_get_person,
                        'people_id': people_id,
                        'people_profile': f'profile: {data["name"]} ({data["id"]})' if data else '',
                        'people_avatar_url': f'{data["avatar_url"]}' if data else ''})

    return HttpResponse(t.render(c))


def app_people_load_all_to_db(request):
    """
    load manually all people data from API to db, access the URL directly (refer to the urls.py)
    :param request:
    :return:
    """

    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get all projects APIa
    response = bc_api_get(uri=api_people_get_all_people_uri(), access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    # print(f'X-Total-Count: {response.headers["X-Total-Count"]}')

    for person in data:
        if person["personable_type"] not in ['DummyUser', 'Tombstone']:
            if not person["employee"] or 'bot' in person["name"]:
                print(person)
            # process company
            if "company" in person and "id" in person["company"]:
                serializer = BcPeopleSerializer(data=person)
                if serializer.is_valid():
                    people = serializer.save()
                    print(f'person {people} loaded.')
                else:  # invalid serializer
                    print(serializer.errors)

            else:
                print(f'person {person["name"]} <{person["email_address"]}> has no company information.')

    total_data = len(data)  # initial total

    if 'next' in response.links and 'url' in response.links["next"]:
        next_url = response.links["next"]["url"]
    else:
        next_url = None

    while next_url:  # as long as next url exists
        response = bc_api_get(uri=next_url, access_token=token["access_token"])

        if response.status_code != 200:  # not OK
            return HttpResponse('', status=response.status_code)

        # if OK
        data = response.json()

        for person in data:
            if person["personable_type"] not in ['DummyUser', 'Tombstone']:
                if not person["employee"] or 'bot' in person["name"]:
                    print(person)
                # process company
                if "company" in person and "id" in person["company"]:
                    serializer = BcPeopleSerializer(data=person)
                    if serializer.is_valid():
                        people = serializer.save()
                        print(f'person {people} loaded.')
                    else:  # invalid serializer
                        print(serializer.errors)

                else:
                    print(f'person {person["name"]} <{person["email_address"]}> has no company information.')

        total_data += len(data)

        if 'next' in response.links and 'url' in response.links["next"]:
            next_url = response.links["next"]["url"]
        else:
            next_url = None

    return HttpResponse(f'load people to db: {total_data}')
