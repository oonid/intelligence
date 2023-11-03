from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_todolist_get_bucket_todoset_todolists_uri,
                      api_todolist_get_bucket_todolist_uri)


def app_todolist_main(request, bucket_id, todoset_id):
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
        print(todolist)
        todolist_list += (f'<li><a href="' + reverse('app-todolist-detail',
                                                     kwargs={'bucket_id': bucket_id, 'todolist_id': todolist["id"]}) +
                          f'">{todolist["id"]}</a> '
                          f'{todolist["title"]} ' +
                          ('(completed) ' if todolist["completed"] else f'({todolist["completed_ratio"]}) ') +
                          f'{todolist["comments_count"]} comments</li>')
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
    data = response.json()
    print(data)

    if 'groups_url' in data:  # type todolist
        todolist_group_str = ('<a href="' + reverse('app-todolist_group-main',
                                                    kwargs={'bucket_id': bucket_id,
                                                            'todolist_id': todolist_id}) + '">todolist_groups</a><br/>')
    elif 'group_position_url' in data:  # type todolist_group
        todolist_group_str = f'group position url: {data["group_position_url"]}<br/>'
    else:
        todolist_group_str = ''

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {data["title"]}<br/>'
        f'comments_count: {data["comments_count"]}<br/>'
        f'parent: {data["parent"]}<br/>'
        f'completed: {data["completed"]}<br/>'
        f'completed_ratio: {data["completed_ratio"]}<br/>'
        f'{todolist_group_str}'
        '<a href="'+reverse('app-todo-main',
                            kwargs={'bucket_id': bucket_id, 'todolist_id': todolist_id})+'">todos</a><br/>'
    )
