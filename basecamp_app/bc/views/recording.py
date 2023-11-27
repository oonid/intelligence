from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_recording_get_recordings_uri,
                      api_recording_get_bucket_recording_parent_comment_uri,
                      static_get_recording_types, static_get_recording_parent_types)
from bc.models import BcProject, BcPeople, BcTodo, BcTodolist, BcComment
from bc.serializers import BcPeopleSerializer


def app_recording_main(request):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    recording_type_list = ""
    for recording_type in static_get_recording_types():
        recording_type_list += ('<li><a href="' +
                                reverse('app-recording-by-type', kwargs={'recording_type': recording_type}) +
                                f'">{recording_type}</a></li>')

    return HttpResponse(
        '<a href="' + reverse('bc-main') + '">back to main</a><br/>'
        f'{recording_type_list}'
    )


def app_recording_by_type(request, recording_type):
    if not recording_type or recording_type not in static_get_recording_types():
        return HttpResponse('')

    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get recordings from all projects API
    response = bc_api_get(uri=api_recording_get_recordings_uri(recording_type=recording_type),
                          access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    recording_total = len(data)
    recording_keys = []
    for recording in data:
        # print(recording)
        recording_keys = recording.keys()

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    return HttpResponse(
        '<a href="' + reverse('app-recording-main') + '">back</a><br/>'
        f'{recording_type}: got {recording_total} of {total_count} recordings (with {len(recording_keys)} keys)<br/>'
        f'{recording_keys}'
    )


def app_project_recording_by_type(request, bucket_id, recording_type):
    if not recording_type or recording_type not in static_get_recording_types():
        return HttpResponse('')

    # load project from db or give recommendation link to save to db first
    try:
        project = BcProject.objects.get(id=bucket_id)
    except BcProject.DoesNotExist:
        return HttpResponse(
            '<a href="' + reverse('app-project-detail-update-db',
                                  kwargs={'project_id': bucket_id}) +
            '">save project to db</a> first.')

    # project exist on db
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get recordings only from specific project API
    response = bc_api_get(uri=api_recording_get_recordings_uri(recording_type=recording_type, bucket=bucket_id),
                          access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    recording_total = len(data)
    recording_keys = []
    recording_list = ""
    for recording in data:

        if recording_type in ['Comment']:

            if ('parent' in recording and recording["parent"]["type"] in static_get_recording_parent_types() and
                    'bucket' in recording and recording["bucket"]["type"] == "Project" and 'creator' in recording):

                # process bucket first, because at processing parent still need a valid bucket
                try:
                    bucket = BcProject.objects.get(id=recording["bucket"]["id"])
                except BcProject.DoesNotExist:
                    # can not insert new Project with limited data of recording["bucket"]
                    return HttpResponseBadRequest(
                        f'bucket not found: {recording["bucket"]}<br/>'
                        '<a href="' + reverse('app-project-detail-update-db',
                                              kwargs={'project_id': recording["bucket"]["id"]}) +
                        '">save project to db</a> first.'
                    )

                if recording['parent']['type'] == 'Todo':
                    # process parent BcTodo
                    try:
                        parent = BcTodo.objects.get(id=recording["parent"]["id"])
                    except BcTodo.DoesNotExist:
                        # can not insert new Todo with limited data of recording["parent"]
                        return HttpResponseBadRequest(
                            f'todo not found: {recording["parent"]}<br/>'
                            '<a href="' + reverse('app-todo-detail',
                                                  kwargs={'bucket_id': recording["bucket"]["id"],
                                                          'todo_id': recording["parent"]["id"]}) +
                            '">try to open todo</a> first.'
                        )
                elif recording['parent']['type'] == 'Todolist':
                    # process parent BcTodolist
                    try:
                        parent = BcTodolist.objects.get(id=recording["parent"]["id"])
                    except BcTodolist.DoesNotExist:
                        # can not insert new Todolist with limited data of recording["parent"]
                        return HttpResponseBadRequest(
                            f'todolist not found: {recording["parent"]}<br/>'
                            '<a href="' + reverse('app-todolist-detail',
                                                  kwargs={'bucket_id': recording["bucket"]["id"],
                                                          'todolist_id': recording["parent"]["id"]}) +
                            '">try to open todolist</a> first.'
                        )


                else:  # condition above has filter the type in to get_recording_parent_types, should never be here
                    parent = None

                # process creator
                try:
                    creator = BcPeople.objects.get(id=recording["creator"]["id"])
                except BcPeople.DoesNotExist:
                    serializer = BcPeopleSerializer(data=recording["creator"])
                    if serializer.is_valid():
                        creator = serializer.save()
                    else:  # invalid serializer
                        return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

                # remove 'bucket' key from recording. key 'bucket' still used in processing parent
                recording.pop('bucket')

                # remove 'parent' key from recording, will use model instance parent instead
                recording.pop('parent')

                # remove 'creator' key from recording, will use model instance creator instead
                recording.pop('creator')

                # process comment
                try:
                    _comment = BcComment.objects.get(id=recording["id"])
                except BcComment.DoesNotExist:
                    _comment = BcComment.objects.create(bucket=bucket, parent=parent, creator=creator, **recording)
                    _comment.save()

                _comment_title = _comment.title if _comment else recording["title"]
                _saved_on_db = " (db)" if _comment else ""
                _parent_comment_uri = reverse('app-project-recording-parent-comment',
                                              kwargs={'bucket_id': bucket.id,
                                                      'parent_id': parent.id})

                recording_list += (f'<li>{recording["id"]} '
                                   f'<a href="{_parent_comment_uri}">parent_comment</a> '
                                   f'{_comment_title} {_saved_on_db}</li>')

            else:
                return HttpResponseBadRequest(
                    f'recording {recording["title"]} has no creator or bucket type Project or parent type in '
                    f'{static_get_recording_parent_types()}')

        # others recording type
        else:
            print(recording.keys())

        recording_keys = recording.keys()

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': project.id}) + '">back</a><br/>'
        f'{recording_type}: got {recording_total} of {total_count} recordings (with {len(recording_keys)} keys)<br/>'
        f'{recording_keys}<br/>'
        f'{recording_list}<br/>'
    )


def app_project_recording_parent_comment(request, bucket_id, parent_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get recording comment API
    api_recording_get_bucket_recording_parent_comment = (
        api_recording_get_bucket_recording_parent_comment_uri(bucket_id=bucket_id, parent_id=parent_id))
    response = bc_api_get(uri=api_recording_get_bucket_recording_parent_comment, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    count = 0
    comment_list = ""
    for comment in data:
        print(comment)

        comment_list += (f'<li><a href="' + reverse('app-comment-detail',
                                                    kwargs={'bucket_id': bucket_id, 'comment_id': comment["id"]}) +
                         f'">{comment["id"]}</a> {comment["title"]}</li>')
        count += 1

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count_str = ''
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])
        total_count_str = f'shows {count}/{total_count} comments'

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'{total_count_str}<br/>'
        f'{comment_list}<br/>'
    )
