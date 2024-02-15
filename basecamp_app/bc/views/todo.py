from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse

from bc.models import BcTodoset, BcTodolist, BcTodo, BcTodoCompletion
from bc.utils import (session_get_token_and_identity, bc_api_get, db_get_bucket, db_get_or_create_person,
                      api_todo_get_bucket_todolist_todos_uri, api_todo_get_bucket_todo_uri,
                      repr_http_response_template_string, repr_template_response_entity_not_found,
                      repr_template_response_entity_creator_bucket_parent, repr_template_response_simple_with_back)


def app_todo_main(request, bucket_id, todolist_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get todos API
    api_todo_get_todos = api_todo_get_bucket_todolist_todos_uri(bucket_id=bucket_id, todolist_id=todolist_id)
    response = bc_api_get(uri=api_todo_get_todos, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    data = response.json()

    count = 0
    todo_list = ""
    for todo in data:

        if ('parent' in todo and todo["parent"]["type"] in ["Todoset", "Todolist"] and
                'bucket' in todo and todo["bucket"]["type"] == "Project" and 'creator' in todo):

            # process todo
            try:
                _todo = BcTodo.objects.get(id=todo["id"])
            except BcTodo.DoesNotExist:
                # save todo only at app_todo_detail
                _todo = None

        else:
            _exception = repr_template_response_entity_creator_bucket_parent(
                entity_type=todo["type"], entity_title=todo["title"], list_parent_types=["Todoset", "Todolist"])
            return HttpResponseBadRequest(_exception)

        _todo_title = _todo.title if _todo else todo["title"]
        _saved_on_db = " (db)" if _todo else ""

        todo_list += (f'<li><a href="' + reverse('app-todo-detail',
                                                 kwargs={'bucket_id': bucket_id, 'todo_id': todo["id"]}) +
                      f'">{todo["id"]}</a> '
                      f'{_todo_title} ' +
                      ('(completed) ' if todo["completed"] else f'(not-complete) ') +
                      f'{todo["comments_count"]} comments {_saved_on_db}</li>')
        count += 1

    # if 'next' in response.links and 'url' in response.links["next"]:
    #     print(response.links["next"]["url"])

    total_count_str = ''
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])
        total_count_str = f'shows {count}/{total_count} todos'

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-todolist-detail', kwargs={'bucket_id': bucket_id, 'todolist_id': todolist_id}),
        body=f'{total_count_str}<br/>{todo_list}')
    return HttpResponse(_response)


def app_todo_detail(request, bucket_id, todo_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get todoset API
    api_todo_get_todo = api_todo_get_bucket_todo_uri(bucket_id=bucket_id, todo_id=todo_id)
    response = bc_api_get(uri=api_todo_get_todo, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    todo = response.json()

    if ('parent' in todo and todo["parent"]["type"] in ["Todoset", "Todolist"] and
            'bucket' in todo and todo["bucket"]["type"] == "Project" and
            'creator' in todo and 'assignees' in todo and 'completion_subscribers' in todo):

        # process bucket first, because at processing parent still need a valid bucket
        _bucket, _exception = db_get_bucket(bucket_id=todo["bucket"]["id"])
        if not _bucket:  # not exists
            return HttpResponseBadRequest(_exception)

        if todo["parent"]["type"] == "Todoset":
            # process parent BcTodoset
            try:
                parent = BcTodoset.objects.get(id=todo["parent"]["id"])
            except BcTodoset.DoesNotExist:
                # can not insert new Todoset with limited data of todolist["parent"]
                _exception = repr_template_response_entity_not_found(
                    entity_id=todo["parent"]["id"], entity_type=todo["parent"]["type"],
                    href=reverse('app-todoset-detail',
                                 kwargs={'bucket_id': todo["bucket"]["id"], 'todoset_id': todo["parent"]["id"]}))
                return HttpResponseBadRequest(_exception)

        elif todo["parent"]["type"] == "Todolist":
            # process parent BcTodolist
            try:
                parent = BcTodolist.objects.get(id=todo["parent"]["id"])
            except BcTodolist.DoesNotExist:
                # can not insert new Todolist with limited data of todolist["parent"]
                _exception = repr_template_response_entity_not_found(
                    entity_id=todo["parent"]["id"], entity_type=todo["parent"]["type"],
                    href=reverse('app-todolist-detail',
                                 kwargs={'bucket_id': todo["bucket"]["id"], 'todolist_id': todo["parent"]["id"]}))
                return HttpResponseBadRequest(_exception)

        else:  # condition above has filter the type in to Todoset or Todolist, should never be here
            parent = None

        # process creator
        _creator, _exception = db_get_or_create_person(person=todo["creator"])
        if not _creator:  # create person error
            return HttpResponseBadRequest(_exception)

        # remove 'bucket' key from todo. key 'bucket' still used in processing parent
        todo.pop('bucket')

        # remove 'parent' key from todo, will use model instance parent instead
        todo.pop('parent')

        # remove 'creator' key from todo, will use model instance creator instead
        todo.pop('creator')

        # process completion if any
        completion = None
        if 'completion' in todo:
            # process completion creator
            _completion_creator, _exception = db_get_or_create_person(person=todo["completion"]["creator"])
            if not _completion_creator:  # create person error
                return HttpResponseBadRequest(_exception)

            # remove 'creator' key from completion, will use model instance creator instead
            todo["completion"].pop('creator')

            # process completion
            completion = BcTodoCompletion.objects.create(creator=_completion_creator, **todo["completion"])
            completion.save()

            # remove 'completion' key from todo
            todo.pop('completion')

        # process assignees
        assignees = []
        for assignee in todo["assignees"]:
            _assignee, _exception = db_get_or_create_person(person=assignee)
            if not _assignee:  # create person error
                return HttpResponseBadRequest(_exception)

            # list of assignee objects, will be appended later as many-to-many
            assignees.append(_assignee)

        # remove 'assignees' key from todo
        todo.pop('assignees')

        # process completion_subscribers
        completion_subscribers = []
        for subscriber in todo["completion_subscribers"]:
            _subscriber, _exception = db_get_or_create_person(person=subscriber)
            if not _subscriber:  # create person error
                return HttpResponseBadRequest(_exception)

            # list of subscriber objects, will be appended later as many-to-many
            completion_subscribers.append(_subscriber)

        # remove 'completion_subscribers' key from todo
        todo.pop('completion_subscribers')

        # process todo
        try:
            _todo = BcTodo.objects.get(id=todo["id"])
        except BcTodo.DoesNotExist:
            if completion:  # completion exists
                _todo = BcTodo.objects.create(parent=parent, bucket=_bucket, creator=_creator, completion=completion,
                                              **todo)
            else:  # undefined completion
                _todo = BcTodo.objects.create(parent=parent, bucket=_bucket, creator=_creator, **todo)

            # save todo model
            _todo.save()

        # set assignees and completion_subscribers
        _todo.assignees.set(assignees)
        _todo.completion_subscribers.set(completion_subscribers)

    else:
        _exception = repr_template_response_entity_creator_bucket_parent(
            entity_type=todo["type"], entity_title=todo["title"], list_parent_types=["Todoset", "Todolist"])
        return HttpResponseBadRequest(_exception)

    assignees_str = [assignee.name for assignee in assignees]
    completion_subscribers_str = [subscriber.name for subscriber in completion_subscribers]

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-project-detail', kwargs={'project_id': bucket_id}),
        body=f'title: {todo["title"]}<br/>'
        f'due_on: {todo["due_on"]}<br/>'
        f'assignees: {assignees_str}<br/>'
        f'completion_subscribers: {completion_subscribers_str}<br/>'
        f'{todo["comments_count"]} comment(s)')
    return HttpResponse(_response)
