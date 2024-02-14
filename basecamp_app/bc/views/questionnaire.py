from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from json import dumps as json_dumps

from bc.models import BcQuestionnaire, BcQuestion, BcQuestionAnswer, BcRecurrenceSchedule
from bc.utils import (session_get_token_and_identity, bc_api_get, db_get_bucket, db_get_or_create_person,
                      api_questionnaire_get_bucket_questionnaire_uri,
                      api_questionnaire_get_bucket_questionnaire_questions_uri,
                      api_questionnaire_get_bucket_question_uri, api_questionnaire_get_bucket_question_answers_uri,
                      api_questionnaire_get_bucket_question_answer_uri,
                      repr_http_response_template_string, repr_template_response_entity_not_found,
                      repr_template_response_entity_creator_bucket_parent,
                      repr_template_response_entity_creator_bucket)


def app_questionnaire_detail(request, bucket_id, questionnaire_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get questionnaire API
    api_questionnaire_get_questionnaire = (
        api_questionnaire_get_bucket_questionnaire_uri(bucket_id=bucket_id, questionnaire_id=questionnaire_id))
    response = bc_api_get(uri=api_questionnaire_get_questionnaire, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    questionnaire = response.json()

    if 'bucket' in questionnaire and questionnaire["bucket"]["type"] == "Project" and 'creator' in questionnaire:

        # process bucket
        _bucket, _exception = db_get_bucket(bucket_id=questionnaire["bucket"]["id"])
        if not _bucket:  # not exists
            return HttpResponseBadRequest(_exception)

        # remove 'bucket' key from questionnaire, will use model instance bucket instead
        questionnaire.pop('bucket')

        # process creator
        _creator, _exception = db_get_or_create_person(person=questionnaire["creator"])
        if not _creator:  # create person error
            return HttpResponseBadRequest(_exception)

        # remove 'creator' key from questionnaire, will use model instance creator instead
        questionnaire.pop('creator')

        # process questionnaire

        try:
            _questionnaire = BcQuestionnaire.objects.get(id=questionnaire["id"])
        except BcQuestionnaire.DoesNotExist:
            _questionnaire = BcQuestionnaire.objects.create(bucket=_bucket, creator=_creator, **questionnaire)
            _questionnaire.save()

    else:
        _exception = repr_template_response_entity_creator_bucket(entity_type=questionnaire["type"],
                                                                  entity_title=questionnaire["title"])
        return HttpResponseBadRequest(_exception)

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_questionnaire.title}<br/>'
        f'type: {questionnaire["type"]}<br/>'
        f'<a href="' + reverse('app-questionnaire-question',
                               kwargs={'bucket_id': bucket_id, 'questionnaire_id': questionnaire_id}) +
        f'">{questionnaire["questions_count"]} questions</a><br/>'
    )


def app_questionnaire_question(request, bucket_id, questionnaire_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get questionnaire question API
    api_questionnaire_get_bucket_questionnaire_question = (
        api_questionnaire_get_bucket_questionnaire_questions_uri(bucket_id=bucket_id,
                                                                 questionnaire_id=questionnaire_id))
    response = bc_api_get(uri=api_questionnaire_get_bucket_questionnaire_question, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    data = response.json()

    question_list = ""
    for question in data:

        # process question
        try:
            _question = BcQuestion.objects.get(id=question["id"])
        except BcQuestion.DoesNotExist:
            # save question only at app_question_detail
            _question = None

        _saved_on_db = " (db)" if _question else ""

        question_list += (f'<li><a href="' + reverse('app-question-detail',
                                                     kwargs={'bucket_id': bucket_id, 'question_id': question["id"]}) +
                          f'">{question["id"]}</a> {question["title"]} {_saved_on_db}</li>')

    # if 'next' in response.links and 'url' in response.links["next"]:
    #     print(response.links["next"]["url"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    total_count_str = f'total questions: {total_count}' if total_count > 0 else ''

    return HttpResponse(
        '<a href="' + reverse('app-questionnaire-detail',
                              kwargs={'bucket_id': bucket_id, 'questionnaire_id': questionnaire_id}) + '">back</a><br/>'
        f'{total_count_str}'
        f'{question_list}')


def app_question_detail(request, bucket_id, question_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get questionnaire question API
    api_questionnaire_get_bucket_question = (
        api_questionnaire_get_bucket_question_uri(bucket_id=bucket_id, question_id=question_id))
    response = bc_api_get(uri=api_questionnaire_get_bucket_question, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    question = response.json()

    if ('parent' in question and question["parent"]["type"] in ["Questionnaire"] and
            'bucket' in question and question["bucket"]["type"] == "Project" and
            'creator' in question and 'schedule' in question):

        # process bucket first, because at processing parent still need a valid bucket
        _bucket, _exception = db_get_bucket(bucket_id=question["bucket"]["id"])
        if not _bucket:  # not exists
            return HttpResponseBadRequest(_exception)

        if question["parent"]["type"] == "Questionnaire":
            # process parent BcQuestionnaire
            try:
                parent = BcQuestionnaire.objects.get(id=question["parent"]["id"])
            except BcQuestionnaire.DoesNotExist:
                # can not insert new Questionnaire with limited data of question["parent"]
                _exception = repr_template_response_entity_not_found(
                    entity_id=question["parent"]["id"], entity_type=question["parent"]["type"],
                    href=reverse('app-questionnaire-detail',
                                 kwargs={'bucket_id': question["bucket"]["id"],
                                         'questionnaire_id': question["parent"]["id"]}))
                return HttpResponseBadRequest(_exception)

        else:  # condition above has filter the type in to Questionnaire, should never be here
            parent = None

        # remove 'parent' key from question, will use model instance parent instead
        question.pop('parent')

        # remove 'bucket' key from question, will use model instance bucket instead
        question.pop('bucket')

        # process creator
        _creator, _exception = db_get_or_create_person(person=question["creator"])
        if not _creator:  # create person error
            return HttpResponseBadRequest(_exception)

        # remove 'creator' key from question, will use model instance creator instead
        question.pop('creator')

        # process question and schedule (because schedule has no id, the only access via ForeignKey)

        try:
            _question = BcQuestion.objects.get(id=question["id"])
        except BcQuestion.DoesNotExist:

            json_days = json_dumps(question["schedule"]["days"])
            question["schedule"].pop('days')
            schedule = BcRecurrenceSchedule.objects.create(days=json_days, **question["schedule"])
            schedule.save()
            # remove 'schedule' key from question, will use model instance question instead
            question.pop('schedule')

            _question = BcQuestion.objects.create(parent=parent, bucket=_bucket, creator=_creator,
                                                  schedule=schedule, **question)
            _question.save()

    else:
        return HttpResponseBadRequest(
            f'question {question["title"]} has no schedule or creator or '
            f'bucket type Project or parent type Questionnaire')

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {question["title"]}<br/>'
        f'type: {question["type"]}<br/>'
        f'<a href="' + reverse('app-question-answer',
                               kwargs={'bucket_id': bucket_id, 'question_id': question["id"]}) +
        f'">{question["answers_count"]} answers</a><br/>'
    )


def app_question_answer(request, bucket_id, question_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get questionnaire question answer API
    api_questionnaire_get_bucket_question_answer = (
        api_questionnaire_get_bucket_question_answers_uri(bucket_id=bucket_id, question_id=question_id))
    response = bc_api_get(uri=api_questionnaire_get_bucket_question_answer, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    data = response.json()

    answer_list = ""
    for answer in data:

        # process question
        try:
            _question_answer = BcQuestionAnswer.objects.get(id=answer["id"])
        except BcQuestionAnswer.DoesNotExist:
            # save todolist only at app_todolist_detail
            _question_answer = None

        _saved_on_db = " (db)" if _question_answer else ""

        answer_list += (f'<li><a href="' +
                        reverse('app-question-answer-detail',
                                kwargs={'bucket_id': bucket_id, 'question_answer_id': answer["id"]}) +
                        f'">{answer["id"]}</a> {answer["title"]}</li>')

    # if 'next' in response.links and 'url' in response.links["next"]:
    #     print(response.links["next"]["url"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    total_count_str = f'total answers: {total_count}' if total_count > 0 else ''

    return HttpResponse(
        '<a href="' + reverse('app-question-detail',
                              kwargs={'bucket_id': bucket_id, 'question_id': question_id}) + '">back</a><br/>'
        f'{total_count_str}'
        f'{answer_list}')


def app_question_answer_detail(request, bucket_id, question_answer_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get questionnaire question answer API
    api_questionnaire_get_bucket_question_answer = (
        api_questionnaire_get_bucket_question_answer_uri(bucket_id=bucket_id, question_answer_id=question_answer_id))
    response = bc_api_get(uri=api_questionnaire_get_bucket_question_answer, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    answer = response.json()

    if ('parent' in answer and answer["parent"]["type"] in ["Question"] and
            'bucket' in answer and answer["bucket"]["type"] == "Project" and 'creator' in answer):

        # process bucket first, because at processing parent still need a valid bucket
        _bucket, _exception = db_get_bucket(bucket_id=answer["bucket"]["id"])
        if not _bucket:  # not exists
            return HttpResponseBadRequest(_exception)

        if answer["parent"]["type"] == "Question":
            # process parent BcQuestion
            try:
                parent = BcQuestion.objects.get(id=answer["parent"]["id"])
            except BcQuestion.DoesNotExist:
                # can not insert new Question with limited data of answer["parent"]
                _exception = repr_template_response_entity_not_found(
                    entity_id=answer["parent"]["id"], entity_type=answer["parent"]["type"],
                    href=reverse('app-question-detail',
                                 kwargs={'bucket_id': answer["bucket"]["id"], 'question_id': answer["parent"]["id"]}))
                return HttpResponseBadRequest(_exception)

        else:  # condition above has filter the type in to Question, should never be here
            parent = None

        # remove 'parent' key from question, will use model instance parent instead
        answer.pop('parent')

        # remove 'bucket' key from answer, will use model instance bucket instead
        answer.pop('bucket')

        # process creator
        _creator, _exception = db_get_or_create_person(person=answer["creator"])
        if not _creator:  # create person error
            return HttpResponseBadRequest(_exception)

        # remove 'creator' key from question, will use model instance creator instead
        answer.pop('creator')

        # process question answer
        try:
            _question_answer = BcQuestionAnswer.objects.get(id=answer["id"])
        except BcQuestionAnswer.DoesNotExist:
            _question_answer = BcQuestionAnswer.objects.create(parent=parent, bucket=_bucket, creator=_creator,
                                                               **answer)
            _question_answer.save()

    else:
        _exception = repr_template_response_entity_creator_bucket_parent(
            entity_type=answer["type"], entity_title=answer["title"], list_parent_types=["Question"])
        return HttpResponseBadRequest(_exception)

    _question_answer_title = _question_answer.title if _question_answer else answer["title"]

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_question_answer_title}<br/>'
        f'type: {answer["type"]}<br/>'
        f'comments_count: {answer["comments_count"]}<br/>'
    )
