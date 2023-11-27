from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_comment_get_bucket_comment_uri,
                      static_get_recording_parent_uri, static_get_recording_parent_types)


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

    else:
        return HttpResponseBadRequest(
            f'comment {comment["title"]} has no creator or bucket type Project or parent type in '
            f'{static_get_recording_parent_types()}')

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {comment["title"]}<br/>'
        f'{parent_str}<br/>'
    )
