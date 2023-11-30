from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse

from bc.models import BcMessageCategory, BcMessageBoard, BcMessage
from bc.utils import (session_get_token_and_identity, bc_api_get, repr_message_detail,
                      db_get_bucket, db_get_message, db_get_or_create_person,
                      api_message_get_bucket_message_types_uri, api_message_get_bucket_message_board_uri,
                      api_message_get_bucket_message_board_messages_uri, api_message_get_bucket_message_uri)


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

        # process message_type
        try:
            _message_category = BcMessageCategory.objects.get(id=message_type["id"])
        except BcMessageCategory.DoesNotExist:
            # save message_category
            _message_category = BcMessageCategory.objects.create(**message_type)
            _message_category.save()

        message_type_list += f'<li>{_message_category.icon} {_message_category.name}</li>'

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

    # request to get message board API
    api_message_get_bucket_message_board = api_message_get_bucket_message_board_uri(bucket_id=bucket_id,
                                                                                    message_board_id=message_board_id)
    response = bc_api_get(uri=api_message_get_bucket_message_board, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    message_board = response.json()

    # process bucket first, because at processing parent still need a valid bucket
    bucket, message = db_get_bucket(bucket_id=message_board["bucket"]["id"])
    if not bucket:  # not exists
        return HttpResponseBadRequest(message)

    # remove 'bucket' key from message_board, will use model instance bucket instead
    message_board.pop('bucket')

    # process creator
    creator, message = db_get_or_create_person(person=message_board["creator"])
    if not creator:  # create person error
        return HttpResponseBadRequest(message)

    # remove 'creator' key from message_board, will use model instance creator instead
    message_board.pop('creator')

    # process message_board
    try:
        _message_board = BcMessageBoard.objects.get(id=message_board["id"])
    except BcMessageBoard.DoesNotExist:
        # save message_board
        _message_board = BcMessageBoard.objects.create(bucket=bucket, creator=creator, **message_board)
        _message_board.save()

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_message_board.title}<br/>'
        f'type: {message_board["type"]}<br/>'
        '<a href="' + reverse('app-message-board-message',
                              kwargs={'bucket_id': bucket_id, 'message_board_id': message_board_id}) +
        f'">{message_board["messages_count"]} messages</a><br/>')


def app_message_board_message(request, bucket_id, message_board_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get message-board messages API
    api_message_get_bucket_message_board_message = (
        api_message_get_bucket_message_board_messages_uri(bucket_id=bucket_id, message_board_id=message_board_id))
    response = bc_api_get(uri=api_message_get_bucket_message_board_message, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    message_list = ""
    for message in data:

        # process bucket first, because at processing parent still need a valid bucket
        bucket, exception = db_get_bucket(bucket_id=message["bucket"]["id"])
        if not bucket:  # not exists
            return HttpResponseBadRequest(exception)

        # check message_board, if not exist on db, save via message_board_detail
        try:
            _message_board = BcMessageBoard.objects.get(id=message_board_id)
        except BcMessageBoard.DoesNotExist:
            # message board save only at message_board_detail
            return HttpResponseBadRequest(
                f'message board not found, id: {message_board_id}<br/>'
                '<a href="' + reverse('app-message-board-detail',
                                      kwargs={'bucket_id': bucket_id,
                                              'message_board_id': message_board_id}) +
                '">try to open message board</a> first.'
            )

        # process message
        _message, exception = db_get_message(message=message, bucket_id=bucket.id)
        # returned _message can be None, currently ignore the exception as we only show the list

        message_list += repr_message_detail(message=message, bucket_id=bucket.id, message_obj=_message, as_list=True)

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


def app_message_detail(request, bucket_id, message_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get message API
    api_message_get_bucket_message = api_message_get_bucket_message_uri(bucket_id=bucket_id, message_id=message_id)
    response = bc_api_get(uri=api_message_get_bucket_message, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    message = response.json()

    if ('parent' in message and message["parent"]["type"] in ["Message::Board"] and
            'bucket' in message and message["bucket"]["type"] == "Project" and 'creator' in message):

        # process bucket first, because at processing parent still need a valid bucket
        bucket, message = db_get_bucket(bucket_id=message["bucket"]["id"])
        if not bucket:  # not exists
            return HttpResponseBadRequest(message)

        # process parent message_board
        if message["parent"]["type"] == "Message::Board":
            try:
                parent = BcMessageBoard.objects.get(id=message["parent"]["id"])
            except BcMessageBoard.DoesNotExist:
                # can not insert new BcMessageBoard with limited data of message["parent"]
                return HttpResponseBadRequest(
                    f'message board not found: {message["parent"]}<br/>'
                    '<a href="' + reverse('app-message-board-detail',
                                          kwargs={'bucket_id': message["bucket"]["id"],
                                                  'message_board_id': message["parent"]["id"]}) +
                    '">try to open message board</a> first.'
                )

        else:  # condition above has filter the type as Message::Board, should never be here
            parent = None

        # remove 'parent' key from message, will use model instance parent instead
        message.pop('parent')

        # remove 'bucket' key from message, will use model instance bucket instead
        message.pop('bucket')

        # process creator
        creator, message = db_get_or_create_person(person=message["creator"])
        if not creator:  # create person error
            return HttpResponseBadRequest(message)

        # remove 'creator' key from message, will use model instance creator instead
        message.pop('creator')

        # process message_category
        if 'category' in message:  # category is optional, so do not need else on this if
            try:
                category = BcMessageCategory.objects.get(id=message["category"]["id"])
            except BcMessageCategory.DoesNotExist:
                # can not insert new Message Category with limited data of message["category"]
                return HttpResponseBadRequest(
                    f'message category not found: {message["category"]}<br/>'
                    '<a href="' + reverse('app-message-type',
                                          kwargs={'bucket_id': bucket_id}) +
                    '">save message types to db</a> first.'
                )

            # remove 'category' key from message, will use model instance of category instead
            message.pop('category')

        else:  # category is optional, if key 'category' not found, set category as None
            category = None

        # process message
        try:
            _message = BcMessage.objects.get(id=message["id"])
        except BcMessage.DoesNotExist:
            # save message
            _message = BcMessage.objects.create(parent=parent, bucket=bucket, creator=creator,
                                                category=category, **message)
            _message.save()

    else:
        return HttpResponseBadRequest(
            f'message {message["title"]} has no creator or bucket type Project or parent type Message::Board')

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_message.title}<br/>'
        f'type: {message["type"]}<br/>'
        f'comments_count: {message["comments_count"]}<br/>'
    )
