from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse

from bc.models import BcTodoset
from bc.utils import (session_get_token_and_identity, bc_api_get, db_get_bucket, db_get_or_create_person,
                      api_todoset_get_bucket_todoset_uri,
                      repr_template_response_entity_creator_bucket, repr_template_response_simple_with_back)


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
        _bucket, _exception = db_get_bucket(bucket_id=todoset["bucket"]["id"])
        if not _bucket:  # not exists
            return HttpResponseBadRequest(_exception)

        # remove 'bucket' key from todoset, will use model instance bucket instead
        todoset.pop('bucket')

        # process creator
        _creator, _exception = db_get_or_create_person(person=todoset["creator"])
        if not _creator:  # create person error
            return HttpResponseBadRequest(_exception)

        # remove 'creator' key from todoset, will use model instance creator instead
        todoset.pop('creator')

        # process todoset
        try:
            _todoset = BcTodoset.objects.get(id=todoset["id"])
        except BcTodoset.DoesNotExist:
            _todoset = BcTodoset.objects.create(bucket=_bucket, creator=_creator, **todoset)
            _todoset.save()

    else:
        _exception = repr_template_response_entity_creator_bucket(entity_type=todoset["type"],
                                                                  entity_title=todoset["title"])
        return HttpResponseBadRequest(_exception)

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-project-detail', kwargs={'project_id': bucket_id}),
        body=f'title: {_todoset.title}<br/>'
             f'name: {_todoset.name}<br/>'
             f'type: {_todoset.type}<br/>'
             f'todolists_count: <a href="'+reverse('app-todolist-main',
                                                   kwargs={'bucket_id': bucket_id, 'todoset_id': todoset_id}) +
             f'">{todoset["todolists_count"]} todolists</a><br/>'
             f'completed: {todoset["completed"]}<br/>'
             f'completed_ratio: {todoset["completed_ratio"]}')
    return HttpResponse(_response)
