from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_message_get_message_types_uri)


def app_message_type(request, bucket_id):

    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get message types API
    api_message_get_message_types = api_message_get_message_types_uri(bucket_id=bucket_id)
    response = bc_api_get(uri=api_message_get_message_types, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    message_type_list = ""
    for message_type in data:
        message_type_list += f'<li>{message_type["icon"]} {message_type["name"]}</li>'

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    total_count_str = f'total projects: {total_count}' if total_count > 0 else ''

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'{total_count_str}'
        f'{message_type_list}')
