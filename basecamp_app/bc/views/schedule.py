from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from json import dumps as json_dumps

from bc.models import BcSchedule, BcScheduleEntry, BcRecurrenceSchedule
from bc.utils import (session_get_token_and_identity, bc_api_get, db_get_bucket, db_get_or_create_person,
                      api_schedule_get_bucket_schedule_uri, api_schedule_get_bucket_schedule_entries_uri,
                      api_schedule_get_bucket_schedule_entry_uri,
                      repr_http_response_template_string, repr_template_response_entity_not_found,
                      repr_template_response_entity_creator_bucket, repr_template_response_simple_with_back)


def app_schedule_detail(request, bucket_id, schedule_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get message board API
    api_schedule_get_bucket_schedule = (
        api_schedule_get_bucket_schedule_uri(bucket_id=bucket_id, schedule_id=schedule_id))
    response = bc_api_get(uri=api_schedule_get_bucket_schedule, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    schedule = response.json()

    if 'bucket' in schedule and schedule["bucket"]["type"] == "Project" and 'creator' in schedule:

        # process bucket
        _bucket, _exception = db_get_bucket(bucket_id=schedule["bucket"]["id"])
        if not _bucket:  # not exists
            return HttpResponseBadRequest(_exception)

        # remove 'bucket' key from schedule, will use model instance bucket instead
        schedule.pop('bucket')

        # process creator
        _creator, _exception = db_get_or_create_person(person=schedule["creator"])
        if not _creator:  # create person error
            return HttpResponseBadRequest(_exception)

        # remove 'creator' key from schedule, will use model instance creator instead
        schedule.pop('creator')

        # process schedule
        try:
            _schedule = BcSchedule.objects.get(id=schedule["id"])
        except BcSchedule.DoesNotExist:
            _schedule = BcSchedule.objects.create(bucket=_bucket, creator=_creator, **schedule)
            _schedule.save()

    else:
        _exception = repr_template_response_entity_creator_bucket(entity_type=schedule["type"],
                                                                  entity_title=schedule["title"])
        return HttpResponseBadRequest(_exception)

    _schedule_title = _schedule.title if _schedule else schedule["title"]

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-project-detail', kwargs={'project_id': bucket_id}),
        body=f'title: {_schedule_title}<br/>'
        f'type: {schedule["type"]}<br/>'
        f'<a href="' + reverse('app-schedule-entry',
                               kwargs={'bucket_id': bucket_id, 'schedule_id': schedule_id}) +
        f'">{schedule["entries_count"]} entries</a>')
    return HttpResponse(_response)


def app_schedule_entry(request, bucket_id, schedule_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get schedule entry API
    api_schedule_get_bucket_schedule_entries = (
        api_schedule_get_bucket_schedule_entries_uri(bucket_id=bucket_id, schedule_id=schedule_id))
    response = bc_api_get(uri=api_schedule_get_bucket_schedule_entries, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

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

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-schedule-detail', kwargs={'bucket_id': bucket_id, 'schedule_id': schedule_id}),
        body=f'{total_count_str}<br/>{entry_list}')
    return HttpResponse(_response)


def app_schedule_entry_detail(request, bucket_id, schedule_entry_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get message API
    api_schedule_get_bucket_schedule_entry = (
        api_schedule_get_bucket_schedule_entry_uri(bucket_id=bucket_id, schedule_entry_id=schedule_entry_id))
    response = bc_api_get(uri=api_schedule_get_bucket_schedule_entry, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    schedule_entry = response.json()

    if ('parent' in schedule_entry and schedule_entry["parent"]["type"] in ["Schedule"] and
            'bucket' in schedule_entry and schedule_entry["bucket"]["type"] == "Project" and
            'creator' in schedule_entry and 'participants' in schedule_entry):

        # process bucket first, because at processing parent still need a valid bucket
        _bucket, _exception = db_get_bucket(bucket_id=schedule_entry["bucket"]["id"])
        if not _bucket:  # not exists
            return HttpResponseBadRequest(_exception)

        if schedule_entry["parent"]["type"] == "Schedule":
            # process parent BcSchedule
            try:
                parent = BcSchedule.objects.get(id=schedule_entry["parent"]["id"])
            except BcSchedule.DoesNotExist:
                # can not insert new Schedule with limited data of schedule_entry["parent"]
                _exception = repr_template_response_entity_not_found(
                    entity_id=schedule_entry["parent"]["id"], entity_type=schedule_entry["parent"]["type"],
                    href=reverse('app-schedule-detail',
                                 kwargs={'bucket_id': schedule_entry["bucket"]["id"],
                                         'schedule_id': schedule_entry["parent"]["id"]}))
                return HttpResponseBadRequest(_exception)

        else:  # condition above has filter the type in to Schedule, should never be here
            parent = None

        # remove 'parent' key from schedule entry, will use model instance parent instead
        schedule_entry.pop('parent')

        # remove 'bucket' key from schedule entry, will use model instance bucket instead
        schedule_entry.pop('bucket')

        # process creator
        _creator, _exception = db_get_or_create_person(person=schedule_entry["creator"])
        if not _creator:  # create person error
            return HttpResponseBadRequest(_exception)

        # remove 'creator' key from schedule entry, will use model instance creator instead
        schedule_entry.pop('creator')

        # process participants
        participants = []
        for participant in schedule_entry["participants"]:

            _participant, _exception = db_get_or_create_person(person=participant)
            if not _participant:  # create person error
                return HttpResponseBadRequest(_exception)

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
                _schedule_entry = BcScheduleEntry.objects.create(parent=parent, bucket=_bucket, creator=_creator,
                                                                 recurrence_schedule=schedule, **schedule_entry)
                _schedule_entry.save()

        else:  # without recurrence schedule

            # process schedule entry
            try:
                _schedule_entry = BcScheduleEntry.objects.get(id=schedule_entry["id"])
            except BcScheduleEntry.DoesNotExist:
                _schedule_entry = BcScheduleEntry.objects.create(parent=parent, bucket=_bucket, creator=_creator,
                                                                 **schedule_entry)
                _schedule_entry.save()

        # set participants
        _schedule_entry.participants.set(participants)

    else:
        return HttpResponseBadRequest(
            f'question {schedule_entry["title"]} has no participants or creator or '
            f'bucket type Project or parent type Schedule')

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-project-detail', kwargs={'project_id': bucket_id}),
        body=f'title: {schedule_entry["title"]}<br/>'
        f'type: {schedule_entry["type"]}<br/>'
        f'starts_at: {schedule_entry["starts_at"]}<br/>'
        f'ends_at: {schedule_entry["ends_at"]}<br/>'
        f'comments_count: {schedule_entry["comments_count"]}')
    return HttpResponse(_response)
