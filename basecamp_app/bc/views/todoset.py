from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_todoset_get_bucket_todoset_uri)


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
    data = response.json()
    print(data)

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {data["title"]}<br/>'
        f'name: {data["name"]}<br/>'
        f'type: {data["type"]}<br/>'
        f'todolists_count: <a href="'+reverse('app-todolist-main',
                                              kwargs={'bucket_id': bucket_id, 'todoset_id': todoset_id}) +
        f'">{data["todolists_count"]}</a><br/>'
        f'completed: {data["completed"]}<br/>'
        f'completed_ratio: {data["completed_ratio"]}<br/>'
    )
