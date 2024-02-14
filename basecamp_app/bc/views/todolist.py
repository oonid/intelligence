from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse

from bc.models import BcTodoset, BcTodolist
from bc.utils import (session_get_token_and_identity, bc_api_get, db_get_bucket, db_get_or_create_person,
                      api_todolist_get_bucket_todoset_todolists_uri, api_todolist_get_bucket_todolist_uri,
                      repr_http_response_template_string, repr_template_response_entity_not_found,
                      repr_template_response_entity_creator_bucket_parent)


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
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

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
            _exception = repr_template_response_entity_creator_bucket_parent(
                entity_type=todolist["type"], entity_title=todolist["title"], list_parent_types=["Todoset", "Todolist"])
            return HttpResponseBadRequest(_exception)

        _todolist_title = _todolist.title if _todolist else todolist["title"]
        _saved_on_db = " (db)" if _todolist else ""

        todolist_list += (f'<li><a href="' + reverse('app-todolist-detail',
                                                     kwargs={'bucket_id': bucket_id, 'todolist_id': todolist["id"]}) +
                          f'">{todolist["id"]}</a> '
                          f'{_todolist_title} ' +
                          ('(completed) ' if todolist["completed"] else f'({todolist["completed_ratio"]}) ') +
                          f'{todolist["comments_count"]} comments {_saved_on_db}</li>')

        count += 1

    # if 'next' in response.links and 'url' in response.links["next"]:
    #     print(response.links["next"]["url"])

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
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    todolist = response.json()

    if ('parent' in todolist and todolist["parent"]["type"] in ["Todoset", "Todolist"] and
            'bucket' in todolist and todolist["bucket"]["type"] == "Project" and 'creator' in todolist):

        # process bucket first, because at processing parent still need a valid bucket
        bucket, message = db_get_bucket(bucket_id=todolist["bucket"]["id"])
        if not bucket:  # not exists
            return HttpResponseBadRequest(message)

        if todolist["parent"]["type"] == "Todoset":
            # process parent BcTodoset
            try:
                parent = BcTodoset.objects.get(id=todolist["parent"]["id"])
            except BcTodoset.DoesNotExist:
                # can not insert new Todoset with limited data of todolist["parent"]
                _exception = repr_template_response_entity_not_found(
                    entity_id=todolist["parent"]["id"], entity_type=todolist["parent"]["type"],
                    href=reverse('app-todoset-detail',
                                 kwargs={'bucket_id': todolist["bucket"]["id"],
                                         'todoset_id': todolist["parent"]["id"]}))
                return HttpResponseBadRequest(_exception)

        elif todolist["parent"]["type"] == "Todolist":
            # process parent BcTodolist
            try:
                parent = BcTodolist.objects.get(id=todolist["parent"]["id"])
            except BcTodolist.DoesNotExist:
                # can not insert new Todolist with limited data of todolist["parent"]
                _exception = repr_template_response_entity_not_found(
                    entity_id=todolist["parent"]["id"], entity_type=todolist["parent"]["type"],
                    href=reverse('app-todolist-detail',
                                 kwargs={'bucket_id': todolist["bucket"]["id"],
                                         'todolist_id': todolist["parent"]["id"]}))
                return HttpResponseBadRequest(_exception)

        else:  # condition above has filter the type in to Todoset or Todolist, should never be here
            parent = None

        # remove 'parent' key from todolist, will use model instance parent instead
        todolist.pop('parent')

        # remove 'bucket' key from todolist, will use model instance bucket instead
        todolist.pop('bucket')

        # process creator
        creator, message = db_get_or_create_person(person=todolist["creator"])
        if not creator:  # create person error
            return HttpResponseBadRequest(message)

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
        _exception = repr_template_response_entity_creator_bucket_parent(
            entity_type=todolist["type"], entity_title=todolist["title"], list_parent_types=["Todoset", "Todolist"])
        return HttpResponseBadRequest(_exception)

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {todolist["title"]}<br/>'
        f'completed: {todolist["completed"]}<br/>'
        f'completed_ratio: {todolist["completed_ratio"]}<br/>'
        f'{todolist_group_str}'
        '<a href="'+reverse('app-todo-main',
                            kwargs={'bucket_id': bucket_id, 'todolist_id': todolist_id})+'">todos</a><br/>'
        f'{todolist["comments_count"]} comment(s)<br/>'
    )
