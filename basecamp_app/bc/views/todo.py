from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_todo_get_todos_uri, api_todo_get_todo_uri)


def app_todo_main(request, bucket_id, todolist_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get todos API
    api_todo_get_todos = api_todo_get_todos_uri(bucket_id=bucket_id, todolist_id=todolist_id)
    print(api_todo_get_todos)
    response = bc_api_get(uri=api_todo_get_todos, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    print(response.status_code)
    print(data)

    count = 0
    todo_list = ""
    for todo in data:
        print(todo)
        todo_list += (f'<li><a href="#">{todo["id"]}</a> '
                      f'{todo["title"]} ' +
                      ('(completed) ' if todo["completed"] else f'(not-complete) ') +
                      f'{todo["comments_count"]} comments</li>')
        count += 1

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count_str = ''
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])
        total_count_str = f'shows {count}/{total_count} todos'

    return HttpResponse(
        '<a href="' + reverse('app-todolist-detail',
                              kwargs={'bucket_id': bucket_id, 'todolist_id': todolist_id}) + '">back</a><br/>'
        f'{total_count_str}<br/>'
        f'{todo_list}<br/>'
    )


def app_todo_detail(request, bucket_id, todo_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get todoset API
    api_todo_get_todo = api_todo_get_todo_uri(bucket_id=bucket_id, todo_id=todo_id)
    response = bc_api_get(uri=api_todo_get_todo, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    print(data)

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {data["title"]}<br/>'
    )
