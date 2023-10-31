from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_recording_get_recordings)


def app_recording_main(request):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    recording_types = ['Comment', 'Document', 'Message', 'Question::Answer', 'Schedule::Entry', 'Todo', 'Todolist',
                       'Upload', 'Vault']

    recording_type_list = ""
    for recording_type in recording_types:
        recording_type_list += ('<li><a href="' +
                                reverse('app-recording-by-type', kwargs={'recording_type': recording_type}) +
                                f'">{recording_type}</a></li>')

    return HttpResponse(
        '<a href="' + reverse('bc-main') + '">back to main</a><br/>'
        f'{recording_type_list}'
    )


def app_recording_by_type(request, recording_type):
    recording_types = ['Comment', 'Document', 'Message', 'Question::Answer', 'Schedule::Entry', 'Todo', 'Todolist',
                       'Upload', 'Vault']
    if not recording_type or recording_type not in recording_types:
        return HttpResponse('')

    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get all projects API
    response = bc_api_get(uri=api_recording_get_recordings(recording_type=recording_type),
                          access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    recording_total = len(data)
    recording_keys = []
    for recording in data:
        # print(recording)
        recording_keys = recording.keys()

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    return HttpResponse(
        '<a href="' + reverse('app-recording-main') + '">back</a><br/>'
        f'{recording_type}: got {recording_total} of {total_count} recordings (with {len(recording_keys)} keys)<br/>'
        f'{recording_keys}'
    )
