from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, db_get_bucket, api_todoset_get_bucket_todoset_uri)
from bc.models import BcPeople, BcTodoset
from bc.serializers import BcPeopleSerializer


def app_todoset_detail(request, bucket_id, todoset_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get todoset API
    api_todoset_get_bucket_todoset = api_todoset_get_bucket_todoset_uri(bucket_id=bucket_id, todoset_id=todoset_id)
    response = bc_api_get(uri=api_todoset_get_bucket_todoset, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    todoset = response.json()

    if 'bucket' in todoset and todoset["bucket"]["type"] == "Project" and 'creator' in todoset:

        # process bucket
        bucket, message = db_get_bucket(bucket_id=todoset["bucket"]["id"])
        if not bucket:  # not exists
            return HttpResponseBadRequest(message)

        # remove 'bucket' key from todoset, will use model instance bucket instead
        todoset.pop('bucket')

        # process creator
        try:
            creator = BcPeople.objects.get(id=todoset["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=todoset["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

        # remove 'creator' key from todoset, will use model instance creator instead
        todoset.pop('creator')

        # process todoset
        try:
            _todoset = BcTodoset.objects.get(id=todoset["id"])
        except BcTodoset.DoesNotExist:
            _todoset = BcTodoset.objects.create(bucket=bucket, creator=creator, **todoset)
            _todoset.save()

    else:
        return HttpResponseBadRequest(f'todoset {todoset["title"]} has no creator or bucket with type Project')

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_todoset.title}<br/>'
        f'name: {_todoset.name}<br/>'
        f'type: {_todoset.type}<br/>'
        f'todolists_count: <a href="'+reverse('app-todolist-main',
                                              kwargs={'bucket_id': bucket_id, 'todoset_id': todoset_id}) +
        f'">{todoset["todolists_count"]} todolists</a><br/>'
        f'completed: {todoset["completed"]}<br/>'
        f'completed_ratio: {todoset["completed_ratio"]}<br/>'
    )
