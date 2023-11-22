from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_schedule_get_bucket_schedule_uri,
                      api_schedule_get_bucket_schedule_entries_uri, api_schedule_get_bucket_schedule_entry_uri)
from bc.models import BcProject, BcPeople, BcSchedule, BcScheduleEntry, BcRecurrenceSchedule
from bc.serializers import BcPeopleSerializer
from json import dumps as json_dumps


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

    if 'bucket' in schedule and schedule["bucket"]["type"] == "Project" and 'creator' in schedule:

        # process bucket
        try:
            bucket = BcProject.objects.get(id=schedule["bucket"]["id"])
        except BcProject.DoesNotExist:
            # can not insert new Project with limited data of schedule["bucket"]
            return HttpResponseBadRequest(
                f'bucket not found: {schedule["bucket"]}<br/>'
                '<a href="' + reverse('app-project-detail-update-db',
                                      kwargs={'project_id': schedule["bucket"]["id"]}) +
                '">save project to db</a> first.'
            )

        # remove 'bucket' key from schedule, will use model instance bucket instead
        schedule.pop('bucket')

        # process creator
        try:
            creator = BcPeople.objects.get(id=schedule["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=schedule["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

        # remove 'creator' key from schedule, will use model instance creator instead
        schedule.pop('creator')

        # process schedule

        try:
            _schedule = BcSchedule.objects.get(id=schedule["id"])
        except BcSchedule.DoesNotExist:
            _schedule = BcSchedule.objects.create(bucket=bucket, creator=creator, **schedule)
            _schedule.save()

    else:
        return HttpResponseBadRequest(
            f'todolist {schedule["title"]} has no creator or bucket type Project')

    _schedule_title = _schedule.title if _schedule else schedule["title"]

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_schedule_title}<br/>'
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

        # process entry
        try:
            _entry = BcScheduleEntry.objects.get(id=entry["id"])
        except BcScheduleEntry.DoesNotExist:
            # save schedule_entry only at app_schedule_entry_detail
            _entry = None

        _saved_on_db = " (db)" if _entry else ""

        entry_list += (f'<li><a href="' + reverse('app-schedule-entry-detail',
                                                  kwargs={'bucket_id': bucket_id, 'schedule_entry_id': entry["id"]}) +
                       f'">{entry["id"]}</a> {entry["title"]} {_saved_on_db}</li>')

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    total_count_str = f'total entries: {total_count}' if total_count > 0 else ''

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

    if ('parent' in schedule_entry and schedule_entry["parent"]["type"] in ["Schedule"] and
            'bucket' in schedule_entry and schedule_entry["bucket"]["type"] == "Project" and
            'creator' in schedule_entry and 'participants' in schedule_entry):

        if schedule_entry["parent"]["type"] == "Schedule":
            # process parent BcSchedule
            try:
                parent = BcSchedule.objects.get(id=schedule_entry["parent"]["id"])
            except BcSchedule.DoesNotExist:
                # can not insert new Schedule with limited data of schedule_entry["parent"]
                return HttpResponseBadRequest(
                    f'schedule not found: {schedule_entry["parent"]}<br/>'
                    '<a href="' + reverse('app-schedule-detail',
                                          kwargs={'bucket_id': schedule_entry["bucket"]["id"],
                                                  'schedule_id': schedule_entry["parent"]["id"]}) +
                    '">try to open schedule</a> first.'
                )

        else:  # condition above has filter the type in to Schedule, should never be here
            parent = None

        # remove 'parent' key from schedule entry, will use model instance parent instead
        schedule_entry.pop('parent')

        # process bucket
        try:
            bucket = BcProject.objects.get(id=schedule_entry["bucket"]["id"])
        except BcProject.DoesNotExist:
            # can not insert new Project with limited data of schedule_entry["bucket"]
            return HttpResponseBadRequest(
                f'bucket not found: {schedule_entry["bucket"]}<br/>'
                '<a href="' + reverse('app-project-detail-update-db',
                                      kwargs={'project_id': schedule_entry["bucket"]["id"]}) +
                '">save project to db</a> first.'
            )

        # remove 'bucket' key from schedule entry, will use model instance bucket instead
        schedule_entry.pop('bucket')

        # process creator
        try:
            creator = BcPeople.objects.get(id=schedule_entry["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=schedule_entry["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

        # remove 'creator' key from schedule entry, will use model instance creator instead
        schedule_entry.pop('creator')

        # process participants
        participants = []
        for participant in schedule_entry["participants"]:
            try:
                _participant = BcPeople.objects.get(id=participant["id"])
            except BcPeople.DoesNotExist:
                serializer = BcPeopleSerializer(data=participant)
                if serializer.is_valid():
                    _participant = serializer.save()
                else:  # invalid serializer
                    return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

            # list of assignee objects, will be appended later as many-to-many
            participants.append(_participant)

        # remove 'participants' key from schedule entry
        schedule_entry.pop('participants')

        # (optional) process recurrence schedule
        if 'recurrence_schedule' in schedule_entry:

            json_days = json_dumps(schedule_entry["recurrence_schedule"]["days"])
            schedule_entry["recurrence_schedule"].pop('days')
            schedule = BcRecurrenceSchedule.objects.create(days=json_days, **schedule_entry["recurrence_schedule"])
            schedule.save()
            # remove 'recurrence_schedule' key from schedule entry, will use model instance question instead
            schedule_entry.pop('recurrence_schedule')

            # process schedule entry
            try:
                _schedule_entry = BcScheduleEntry.objects.get(id=schedule_entry["id"])
            except BcScheduleEntry.DoesNotExist:
                _schedule_entry = BcScheduleEntry.objects.create(parent=parent, bucket=bucket, creator=creator,
                                                                 recurrence_schedule=schedule, **schedule_entry)
                _schedule_entry.save()

        else:  # without recurrence schedule

            # process schedule entry
            try:
                _schedule_entry = BcScheduleEntry.objects.get(id=schedule_entry["id"])
            except BcScheduleEntry.DoesNotExist:
                _schedule_entry = BcScheduleEntry.objects.create(parent=parent, bucket=bucket, creator=creator,
                                                                 **schedule_entry)
                _schedule_entry.save()

        # set participants
        _schedule_entry.participants.set(participants)

    else:
        return HttpResponseBadRequest(
            f'question {schedule_entry["title"]} has no participants or creator or '
            f'bucket type Project or parent type Schedule')

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {schedule_entry["title"]}<br/>'
        f'type: {schedule_entry["type"]}<br/>'
        f'starts_at: {schedule_entry["starts_at"]}<br/>'
        f'ends_at: {schedule_entry["ends_at"]}<br/>'
        f'comments_count: {schedule_entry["comments_count"]}<br/>'
    )
