from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_comment_get_bucket_comment_uri,
                      static_get_recording_parent_uri, static_get_recording_parent_types)
from bc.models import BcProject, BcTodo, BcTodolist, BcPeople, BcComment
from bc.serializers import BcPeopleSerializer


def app_comment_detail(request, bucket_id, comment_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get comment API
    api_todo_get_bucket_comment = api_comment_get_bucket_comment_uri(bucket_id=bucket_id, comment_id=comment_id)
    response = bc_api_get(uri=api_todo_get_bucket_comment, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    comment = response.json()
    print(comment)

    if ('parent' in comment and comment["parent"]["type"] in static_get_recording_parent_types() and
            'bucket' in comment and comment["bucket"]["type"] == "Project" and 'creator' in comment):

        parent_uri = static_get_recording_parent_uri(parent=comment["parent"], bucket=comment["bucket"])
        parent_str = (f'parent: <a href="{parent_uri}" target="_black">{comment["parent"]["type"]} '
                      f'{comment["parent"]["id"]}</a>')

        # process bucket first, because at processing parent still need a valid bucket
        try:
            bucket = BcProject.objects.get(id=comment["bucket"]["id"])
        except BcProject.DoesNotExist:
            # can not insert new Project with limited data of recording["bucket"]
            return HttpResponseBadRequest(
                f'bucket not found: {comment["bucket"]}<br/>'
                '<a href="' + reverse('app-project-detail-update-db',
                                      kwargs={'project_id': comment["bucket"]["id"]}) +
                '">save project to db</a> first.'
            )

        if comment['parent']['type'] == 'Todo':
            # process parent BcTodo
            try:
                parent = BcTodo.objects.get(id=comment["parent"]["id"])
            except BcTodo.DoesNotExist:
                # can not insert new Todo with limited data of recording["parent"]
                return HttpResponseBadRequest(
                    f'todo not found: {comment["parent"]}<br/>'
                    '<a href="' + reverse('app-todo-detail',
                                          kwargs={'bucket_id': comment["bucket"]["id"],
                                                  'todo_id': comment["parent"]["id"]}) +
                    '">try to open todo</a> first.'
                )
        elif comment['parent']['type'] == 'Todolist':
            # process parent BcTodolist
            try:
                parent = BcTodolist.objects.get(id=comment["parent"]["id"])
            except BcTodolist.DoesNotExist:
                # can not insert new Todolist with limited data of recording["parent"]
                return HttpResponseBadRequest(
                    f'todolist not found: {comment["parent"]}<br/>'
                    '<a href="' + reverse('app-todolist-detail',
                                          kwargs={'bucket_id': comment["bucket"]["id"],
                                                  'todolist_id': comment["parent"]["id"]}) +
                    '">try to open todolist</a> first.'
                )


        else:  # condition above has filter the type in to get_recording_parent_types, should never be here
            parent = None

        # process creator
        try:
            creator = BcPeople.objects.get(id=comment["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=comment["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

        # remove 'bucket' key from comment. key 'bucket' still used in processing parent
        comment.pop('bucket')

        # remove 'parent' key from comment, will use model instance parent instead
        comment.pop('parent')

        # remove 'creator' key from comment, will use model instance creator instead
        comment.pop('creator')

        # process comment
        try:
            _comment = BcComment.objects.get(id=comment["id"])
        except BcComment.DoesNotExist:
            _comment = BcComment.objects.create(bucket=bucket, parent=parent, creator=creator, **comment)
            _comment.save()

    else:
        return HttpResponseBadRequest(
            f'comment {comment["title"]} has no creator or bucket type Project or parent type in '
            f'{static_get_recording_parent_types()}')

    _comment_title = _comment.title if _comment else comment["title"]

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_comment_title}<br/>'
        f'{parent_str}<br/>'
    )
