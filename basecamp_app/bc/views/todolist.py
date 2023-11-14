from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_todolist_get_bucket_todoset_todolists_uri,
                      api_todolist_get_bucket_todolist_uri)
from bc.models import BcTodoset, BcProject, BcPeople, BcTodolist
from bc.serializers import BcPeopleSerializer


def app_todolist_main(request, bucket_id, todoset_id):
    """

    :param request:
    :param bucket_id:
    :param todoset_id: the parameter is todolist_id, can not todolist_group_id, because todolist_group has different API
    :return:
    """
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get todolist API
    api_todolist_get_bucket_todoset_todolists = (
        api_todolist_get_bucket_todoset_todolists_uri(bucket_id=bucket_id, todoset_id=todoset_id))
    response = bc_api_get(uri=api_todolist_get_bucket_todoset_todolists, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    count = 0
    todolist_list = ""
    for todolist in data:

        if ('parent' in todolist and todolist["parent"]["type"] in ["Todoset", "Todolist"] and
                'bucket' in todolist and todolist["bucket"]["type"] == "Project" and 'creator' in todolist):

            # process todolist
            try:
                _todolist = BcTodolist.objects.get(id=todolist["id"])
            except BcTodolist.DoesNotExist:
                # save todolist only at app_todolist_detail
                _todolist = None

        else:
            return HttpResponseBadRequest(
                f'todolist {todolist["title"]} has no creator or bucket type Project or parent type Todoset/Todolist')

        _todolist_title = _todolist.title if _todolist else todolist["title"]
        _saved_on_db = " (db)" if _todolist else ""

        todolist_list += (f'<li><a href="' + reverse('app-todolist-detail',
                                                     kwargs={'bucket_id': bucket_id, 'todolist_id': todolist["id"]}) +
                          f'">{todolist["id"]}</a> '
                          f'{_todolist_title} ' +
                          ('(completed) ' if todolist["completed"] else f'({todolist["completed_ratio"]}) ') +
                          f'{todolist["comments_count"]} comments {_saved_on_db}</li>')

        count += 1

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count_str = ''
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])
        total_count_str = f'shows {count}/{total_count} todolists'

    return HttpResponse(
        '<a href="' + reverse('app-todoset-detail',
                              kwargs={'bucket_id': bucket_id, 'todoset_id': todoset_id}) + '">back</a><br/>'
        f'{total_count_str}'
        f'{todolist_list}'
    )


def app_todolist_detail(request, bucket_id, todolist_id):
    """

    :param request:
    :param bucket_id:
    :param todolist_id: this parameter can be todolist_id or todolist_group_id
    :return:
    """
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get todolist API
    api_todolist_get_bucket_todolist = (
        api_todolist_get_bucket_todolist_uri(bucket_id=bucket_id, todolist_id=todolist_id))
    response = bc_api_get(uri=api_todolist_get_bucket_todolist, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    todolist = response.json()

    if ('parent' in todolist and todolist["parent"]["type"] in ["Todoset", "Todolist"] and
            'bucket' in todolist and todolist["bucket"]["type"] == "Project" and 'creator' in todolist):

        if todolist["parent"]["type"] == "Todoset":
            # process parent BcTodoset
            try:
                parent = BcTodoset.objects.get(id=todolist["parent"]["id"])
            except BcTodoset.DoesNotExist:
                # can not insert new Todoset with limited data of todolist["parent"]
                return HttpResponseBadRequest(
                    f'todoset not found: {todolist["parent"]}<br/>'
                    '<a href="' + reverse('app-todoset-detail',
                                          kwargs={'bucket_id': todolist["bucket"]["id"],
                                                  'todoset_id': todolist["parent"]["id"]}) +
                    '">try to open todoset</a> first.'
                )

        elif todolist["parent"]["type"] == "Todolist":
            # process parent BcTodolist
            try:
                parent = BcTodolist.objects.get(id=todolist["parent"]["id"])
            except BcTodolist.DoesNotExist:
                # can not insert new Todolist with limited data of todolist["parent"]
                return HttpResponseBadRequest(
                    f'todolist not found: {todolist["parent"]}<br/>'
                    '<a href="' + reverse('app-todolist-detail',
                                          kwargs={'bucket_id': todolist["bucket"]["id"],
                                                  'todolist_id': todolist["parent"]["id"]}) +
                    '">try to open todolist</a> first.'
                )

        else:  # condition above has filter the type in to Todoset or Todolist, should never be here
            parent = None

        # remove 'parent' key from todolist, will use model instance parent instead
        todolist.pop('parent')

        # process bucket
        try:
            bucket = BcProject.objects.get(id=todolist["bucket"]["id"])
        except BcProject.DoesNotExist:
            # can not insert new Project with limited data of todolist["bucket"]
            return HttpResponseBadRequest(
                f'bucket not found: {todolist["bucket"]}<br/>'
                '<a href="' + reverse('app-project-detail-update-db',
                                      kwargs={'project_id': todolist["bucket"]["id"]}) +
                '">save project to db</a> first.'
            )

        # remove 'bucket' key from todolist, will use model instance bucket instead
        todolist.pop('bucket')

        # process creator
        try:
            creator = BcPeople.objects.get(id=todolist["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=todolist["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

        # remove 'creator' key from todolist, will use model instance creator instead
        todolist.pop('creator')

        # process todolist

        if 'groups_url' in todolist:  # type todolist
            is_todolist_group = False
            todolist_group_str = ('<a href="' +
                                  reverse('app-todolist_group-main',
                                          kwargs={'bucket_id': bucket_id,
                                                  'todolist_id': todolist_id}) + '">todolist_groups</a><br/>')

        elif 'group_position_url' in todolist:  # type todolist_group
            is_todolist_group = True
            todolist_group_str = f'group position url: {todolist["group_position_url"]}<br/>'

        else:  # unknown type
            return HttpResponseBadRequest(f'todolist type unknown no groups_url or group_position_url')

        try:
            _todolist = BcTodolist.objects.get(id=todolist["id"])
        except BcTodolist.DoesNotExist:
            _todolist = BcTodolist.objects.create(parent=parent, bucket=bucket, creator=creator,
                                                  is_todolist_group=is_todolist_group, **todolist)
            _todolist.save()

    else:
        return HttpResponseBadRequest(
            f'todolist {todolist["title"]} has no creator or bucket type Project or parent type Todoset/Todolist')

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {todolist["title"]}<br/>'
        f'comments_count: {todolist["comments_count"]}<br/>'
        f'completed: {todolist["completed"]}<br/>'
        f'completed_ratio: {todolist["completed_ratio"]}<br/>'
        f'{todolist_group_str}'
        '<a href="'+reverse('app-todo-main',
                            kwargs={'bucket_id': bucket_id, 'todolist_id': todolist_id})+'">todos</a><br/>'
    )
