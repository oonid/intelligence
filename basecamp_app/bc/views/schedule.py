from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_schedule_get_bucket_schedule_uri,
                      api_schedule_get_bucket_schedule_entries_uri, api_schedule_get_bucket_schedule_entry_uri)


def app_schedule_detail(request, bucket_id, schedule_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get message board API
    api_schedule_get_bucket_schedule = (
        api_schedule_get_bucket_schedule_uri(bucket_id=bucket_id, schedule_id=schedule_id))
    response = bc_api_get(uri=api_schedule_get_bucket_schedule, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    schedule = response.json()
    print(schedule)
    print(schedule.keys())

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {schedule["title"]}<br/>'
        f'type: {schedule["type"]}<br/>'
        f'<a href="' + reverse('app-schedule-entry',
                               kwargs={'bucket_id': bucket_id, 'schedule_id': schedule_id}) +
        f'">{schedule["entries_count"]} entries</a><br/>'
    )


def app_schedule_entry(request, bucket_id, schedule_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get schedule entry API
    api_schedule_get_bucket_schedule_entries = (
        api_schedule_get_bucket_schedule_entries_uri(bucket_id=bucket_id, schedule_id=schedule_id))
    response = bc_api_get(uri=api_schedule_get_bucket_schedule_entries, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    entry_list = ""
    for entry in data:
        print(entry)
        print(entry.keys())

        _saved_on_db = ""

        entry_list += (f'<li><a href="' + reverse('app-schedule-entry-detail',
                                                  kwargs={'bucket_id': bucket_id, 'schedule_entry_id': entry["id"]}) +
                       f'">{entry["id"]}</a> {entry["title"]} {_saved_on_db}</li>')

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    total_count_str = f'total questions: {total_count}' if total_count > 0 else ''

    return HttpResponse(
        '<a href="' + reverse('app-schedule-detail',
                              kwargs={'bucket_id': bucket_id, 'schedule_id': schedule_id}) + '">back</a><br/>'
        f'{total_count_str}'
        f'{entry_list}')


def app_schedule_entry_detail(request, bucket_id, schedule_entry_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get message API
    api_schedule_get_bucket_schedule_entry = (
        api_schedule_get_bucket_schedule_entry_uri(bucket_id=bucket_id, schedule_entry_id=schedule_entry_id))
    response = bc_api_get(uri=api_schedule_get_bucket_schedule_entry, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    schedule_entry = response.json()
    print(schedule_entry)
    print(schedule_entry.keys())

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {schedule_entry["title"]}<br/>'
        f'type: {schedule_entry["type"]}<br/>'
        f'comments_count: {schedule_entry["comments_count"]}<br/>'
    )
