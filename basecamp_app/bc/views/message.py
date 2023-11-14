from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_message_get_bucket_message_types_uri,
                      api_message_get_bucket_message_board_uri, api_message_get_bucket_message_board_message_uri)


def app_message_type(request, bucket_id):

    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get message types API
    api_message_get_message_types = api_message_get_bucket_message_types_uri(bucket_id=bucket_id)
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


def app_message_board_detail(request, bucket_id, message_board_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get message board
    api_message_get_bucket_message_board = api_message_get_bucket_message_board_uri(bucket_id=bucket_id,
                                                                                    message_board_id=message_board_id)
    response = bc_api_get(uri=api_message_get_bucket_message_board, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    message_board = response.json()
    print(message_board)

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {message_board["title"]}<br/>'
        f'type: {message_board["type"]}<br/>'
        f'message_count: {message_board["messages_count"]}<br/>'
        '<a href="' + reverse('app-message-board-message',
                              kwargs={'bucket_id': bucket_id, 'message_board_id': message_board_id}) +
        '">messages</a><br/>')


def app_message_board_message(request, bucket_id, message_board_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get message-board messages API
    api_message_get_bucket_message_board_message = (
        api_message_get_bucket_message_board_message_uri(bucket_id=bucket_id, message_board_id=message_board_id))
    response = bc_api_get(uri=api_message_get_bucket_message_board_message, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    message_list = ""
    for message in data:
        print(message)
        print(message.keys())
        message_list += f'<li><a href="#"">{message["id"]}</a> {message["title"]}</li>'

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    total_count_str = f'total messages: {total_count}' if total_count > 0 else ''

    return HttpResponse(
        '<a href="' + reverse('app-message-board-detail',
                              kwargs={'bucket_id': bucket_id, 'message_board_id': message_board_id}) + '">back</a><br/>'
        f'{total_count_str}'
        f'{message_list}')
