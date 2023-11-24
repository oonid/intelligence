from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_todo_get_bucket_todolist_todos_uri,
                      api_todo_get_bucket_todo_uri)
from bc.models import BcTodoset, BcProject, BcPeople, BcTodolist, BcTodo, BcTodoCompletion
from bc.serializers import BcPeopleSerializer


def app_todo_main(request, bucket_id, todolist_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get todos API
    api_todo_get_todos = api_todo_get_bucket_todolist_todos_uri(bucket_id=bucket_id, todolist_id=todolist_id)
    response = bc_api_get(uri=api_todo_get_todos, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

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
            return HttpResponseBadRequest(
                f'todolist {todo["title"]} has no creator or bucket type Project or parent type Todoset/Todolist')

        _todo_title = _todo.title if _todo else todo["title"]
        _saved_on_db = " (db)" if _todo else ""

        todo_list += (f'<li><a href="' + reverse('app-todo-detail',
                                                 kwargs={'bucket_id': bucket_id, 'todo_id': todo["id"]}) +
                      f'">{todo["id"]}</a> '
                      f'{_todo_title} ' +
                      ('(completed) ' if todo["completed"] else f'(not-complete) ') +
                      f'{todo["comments_count"]} comments {_saved_on_db}</li>')
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
    api_todo_get_todo = api_todo_get_bucket_todo_uri(bucket_id=bucket_id, todo_id=todo_id)
    response = bc_api_get(uri=api_todo_get_todo, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    todo = response.json()

    if ('parent' in todo and todo["parent"]["type"] in ["Todoset", "Todolist"] and
            'bucket' in todo and todo["bucket"]["type"] == "Project" and
            'creator' in todo and 'assignees' in todo and 'completion_subscribers' in todo):

        # process bucket
        try:
            bucket = BcProject.objects.get(id=todo["bucket"]["id"])
        except BcProject.DoesNotExist:
            # can not insert new Project with limited data of todolist["bucket"]
            return HttpResponseBadRequest(
                f'bucket not found: {todo["bucket"]}<br/>'
                '<a href="' + reverse('app-project-detail-update-db',
                                      kwargs={'project_id': todo["bucket"]["id"]}) +
                '">save project to db</a> first.'
            )

        if todo["parent"]["type"] == "Todoset":
            # process parent BcTodoset
            try:
                parent = BcTodoset.objects.get(id=todo["parent"]["id"])
            except BcTodoset.DoesNotExist:
                # can not insert new Todoset with limited data of todolist["parent"]
                return HttpResponseBadRequest(
                    f'todoset not found: {todo["parent"]}<br/>'
                    '<a href="' + reverse('app-todoset-detail',
                                          kwargs={'bucket_id': todo["bucket"]["id"],
                                                  'todoset_id': todo["parent"]["id"]}) +
                    '">try to open todoset</a> first.'
                )

        elif todo["parent"]["type"] == "Todolist":
            # process parent BcTodolist
            try:
                parent = BcTodolist.objects.get(id=todo["parent"]["id"])
            except BcTodolist.DoesNotExist:
                # can not insert new Todolist with limited data of todolist["parent"]
                return HttpResponseBadRequest(
                    f'todolist not found: {todo["parent"]}<br/>'
                    '<a href="' + reverse('app-todolist-detail',
                                          kwargs={'bucket_id': todo["bucket"]["id"],
                                                  'todolist_id': todo["parent"]["id"]}) +
                    '">try to open todolist</a> first.'
                )

        else:  # condition above has filter the type in to Todoset or Todolist, should never be here
            parent = None

        # process creator
        try:
            creator = BcPeople.objects.get(id=todo["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=todo["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

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
            try:
                completion_creator = BcPeople.objects.get(id=todo["completion"]["creator"]["id"])
            except BcPeople.DoesNotExist:
                serializer = BcPeopleSerializer(data=todo["completion"]["creator"])
                if serializer.is_valid():
                    completion_creator = serializer.save()
                else:  # invalid serializer
                    return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

            # remove 'creator' key from completion, will use model instance creator instead
            todo["completion"].pop('creator')

            # process completion
            completion = BcTodoCompletion.objects.create(creator=completion_creator, **todo["completion"])
            completion.save()

            # remove 'completion' key from todo
            todo.pop('completion')

        # process assignees
        assignees = []
        for assignee in todo["assignees"]:
            try:
                _assignee = BcPeople.objects.get(id=assignee["id"])
            except BcPeople.DoesNotExist:
                serializer = BcPeopleSerializer(data=assignee)
                if serializer.is_valid():
                    _assignee = serializer.save()
                else:  # invalid serializer
                    return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

            # list of assignee objects, will be appended later as many-to-many
            assignees.append(_assignee)

        # remove 'assignees' key from todo
        todo.pop('assignees')

        # process completion_subscribers
        completion_subscribers = []
        for subscriber in todo["completion_subscribers"]:
            try:
                _subscriber = BcPeople.objects.get(id=subscriber["id"])
            except BcPeople.DoesNotExist:
                serializer = BcPeopleSerializer(data=subscriber)
                if serializer.is_valid():
                    _subscriber = serializer.save()
                else:  # invalid serializer
                    return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

            # list of subscriber objects, will be appended later as many-to-many
            completion_subscribers.append(_subscriber)

        # remove 'completion_subscribers' key from todo
        todo.pop('completion_subscribers')

        # process todo
        try:
            _todo = BcTodo.objects.get(id=todo["id"])
        except BcTodo.DoesNotExist:
            if completion:  # completion exists
                _todo = BcTodo.objects.create(parent=parent, bucket=bucket, creator=creator, completion=completion,
                                              **todo)
            else:  # undefined completion
                _todo = BcTodo.objects.create(parent=parent, bucket=bucket, creator=creator, **todo)

            # save todo model
            _todo.save()

        # set assignees and completion_subscribers
        _todo.assignees.set(assignees)
        _todo.completion_subscribers.set(completion_subscribers)

    else:
        return HttpResponseBadRequest(
            f'todo {todo["title"]} has no creator or bucket type Project or parent type Todoset/Todolist')

    assignees_str = [assignee.name for assignee in assignees]
    completion_subscribers_str = [subscriber.name for subscriber in completion_subscribers]

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {todo["title"]}<br/>'
        f'due_on: {todo["due_on"]}<br/>'
        f'assignees: {assignees_str}<br/>'
        f'completion_subscribers: {completion_subscribers_str}<br/>'
    )
