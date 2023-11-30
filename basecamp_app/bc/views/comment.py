from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse

from bc.models import BcComment
from bc.utils import (session_get_token_and_identity, bc_api_get,
                      db_get_bucket, db_get_comment_parent, db_get_or_create_person,
                      api_comment_get_bucket_comment_uri,
                      static_get_comment_parent_uri, static_get_comment_parent_types)


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

    if ('parent' in comment and comment["parent"]["type"] in static_get_comment_parent_types() and
            'bucket' in comment and comment["bucket"]["type"] == "Project" and 'creator' in comment):

        parent_uri = static_get_comment_parent_uri(parent=comment["parent"], bucket=comment["bucket"])
        parent_str = (f'parent: <a href="{parent_uri}" target="_black">{comment["parent"]["type"]} '
                      f'{comment["parent"]["id"]}</a>')

        # process bucket first, because at processing parent still need a valid bucket
        bucket, message = db_get_bucket(bucket_id=comment["bucket"]["id"])
        if not bucket:  # not exists
            return HttpResponseBadRequest(message)

        # process parent with type listed in static_get_recording_parent_types
        parent, message = db_get_comment_parent(parent=comment["parent"], bucket_id=comment["bucket"]["id"])
        if not parent:  # not exists
            return HttpResponseBadRequest(message)

        # process creator
        creator, message = db_get_or_create_person(person=comment["creator"])
        if not creator:  # create person error
            return HttpResponseBadRequest(message)

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
            f'{static_get_comment_parent_types()}')

    _comment_title = _comment.title if _comment else comment["title"]

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_comment_title}<br/>'
        f'{parent_str}<br/>'
    )
