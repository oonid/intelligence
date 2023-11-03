from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_todo_get_todos_uri,
                      api_todolist_group_get_todolist_group_uri)


def app_todolist_group_main(request, bucket_id, todolist_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get todolist_group API
    api_todolist_group_get_todolist_group = api_todolist_group_get_todolist_group_uri(bucket_id=bucket_id,
                                                                                      todolist_id=todolist_id)
    response = bc_api_get(uri=api_todolist_group_get_todolist_group, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    count = 0

    todolist_group_list = ""
    for todolist_group in data:
        print(todolist_group)
        # process todolist_group as todolist
        todolist_group_list += (f'<li><a href="' +
                                reverse('app-todolist-detail',
                                        kwargs={'bucket_id': bucket_id, 'todolist_id': todolist_group["id"]}) +
                                f'">{todolist_group["id"]}</a> '
                                f'{todolist_group["title"]} ' +
                                ('(completed) ' if todolist_group["completed"] else
                                 f'({todolist_group["completed_ratio"]}) ') +
                                f'{todolist_group["comments_count"]} comments</li>')
        count += 1

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count_str = ''
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])
        total_count_str = f'shows {count}/{total_count} todolist_groups'

    return HttpResponse(
        '<a href="' + reverse('app-todolist-detail',
                              kwargs={'bucket_id': bucket_id, 'todolist_id': todolist_id}) + '">back</a><br/>'
        f'{total_count_str}<br/>'
        f'{todolist_group_list}<br/>'
    )
