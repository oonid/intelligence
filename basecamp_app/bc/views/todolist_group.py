from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse

from bc.models import BcTodolist
from bc.utils import (session_get_token_and_identity, bc_api_get, api_todolist_group_get_todolist_groups_uri,
                      repr_http_response_template_string, repr_template_response_entity_creator_bucket_parent)


def app_todolist_group_main(request, bucket_id, todolist_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get todolist_group API
    api_todolist_group_get_todolist_group = api_todolist_group_get_todolist_groups_uri(bucket_id=bucket_id,
                                                                                       todolist_id=todolist_id)
    response = bc_api_get(uri=api_todolist_group_get_todolist_group, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    data = response.json()

    count = 0
    todolist_group_list = ""
    for todolist_group in data:

        if ('parent' in todolist_group and todolist_group["parent"]["type"] in ["Todoset", "Todolist"] and
                'bucket' in todolist_group and todolist_group["bucket"]["type"] == "Project" and
                'creator' in todolist_group):

            # process todolist_group as todolist
            try:
                _todolist_group = BcTodolist.objects.get(id=todolist_group["id"])
            except BcTodolist.DoesNotExist:
                # save todolist_group only at app_todolist_group_detail
                _todolist_group = None

        else:
            _exception = repr_template_response_entity_creator_bucket_parent(
                entity_type=todolist_group["type"], entity_title=todolist_group["title"],
                list_parent_types=["Todoset", "Todolist"])
            return HttpResponseBadRequest(_exception)

        _todolist_group_title = _todolist_group.title if _todolist_group else todolist_group["title"]
        _saved_on_db = " (db)" if _todolist_group else ""

        # process todolist_group as todolist
        todolist_group_list += (f'<li><a href="' +
                                reverse('app-todolist-detail',
                                        kwargs={'bucket_id': bucket_id, 'todolist_id': todolist_group["id"]}) +
                                f'">{todolist_group["id"]}</a> '
                                f'{_todolist_group_title} ' +
                                ('(completed) ' if todolist_group["completed"] else
                                 f'({todolist_group["completed_ratio"]}) ') +
                                f'{todolist_group["comments_count"]} comments {_saved_on_db}</li>')
        count += 1

    # if 'next' in response.links and 'url' in response.links["next"]:
    #     print(response.links["next"]["url"])

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
