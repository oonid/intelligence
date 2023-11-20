from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, api_questionnaire_get_bucket_questionnaire_uri,
                      api_questionnaire_get_bucket_questionnaire_questions_uri,
                      api_questionnaire_get_bucket_question_uri, api_questionnaire_get_bucket_question_answers_uri,
                      api_questionnaire_get_bucket_question_answer_uri)
from bc.models import BcProject, BcPeople, BcQuestionnaire, BcQuestion, BcQuestionSchedule, BcQuestionAnswer
from bc.serializers import BcPeopleSerializer
from json import dumps as json_dumps


def app_questionnaire_detail(request, bucket_id, questionnaire_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get message board API
    api_questionnaire_get_questionnaire = (
        api_questionnaire_get_bucket_questionnaire_uri(bucket_id=bucket_id, questionnaire_id=questionnaire_id))
    response = bc_api_get(uri=api_questionnaire_get_questionnaire, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    questionnaire = response.json()
    print(questionnaire)
    print(questionnaire.keys())

    if 'bucket' in questionnaire and questionnaire["bucket"]["type"] == "Project" and 'creator' in questionnaire:

        # process bucket
        try:
            bucket = BcProject.objects.get(id=questionnaire["bucket"]["id"])
        except BcProject.DoesNotExist:
            # can not insert new Project with limited data of todolist["bucket"]
            return HttpResponseBadRequest(
                f'bucket not found: {questionnaire["bucket"]}<br/>'
                '<a href="' + reverse('app-project-detail-update-db',
                                      kwargs={'project_id': questionnaire["bucket"]["id"]}) +
                '">save project to db</a> first.'
            )

        # remove 'bucket' key from questionnaire, will use model instance bucket instead
        questionnaire.pop('bucket')

        # process creator
        try:
            creator = BcPeople.objects.get(id=questionnaire["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=questionnaire["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

        # remove 'creator' key from questionnaire, will use model instance creator instead
        questionnaire.pop('creator')

        # process questionnaire

        try:
            _questionnaire = BcQuestionnaire.objects.get(id=questionnaire["id"])
        except BcQuestionnaire.DoesNotExist:
            _questionnaire = BcQuestionnaire.objects.create(bucket=bucket, creator=creator, **questionnaire)
            _questionnaire.save()

    else:
        return HttpResponseBadRequest(
            f'todolist {questionnaire["title"]} has no creator or bucket type Project')

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

    # request to get message board API
    api_questionnaire_get_bucket_questionnaire_question = (
        api_questionnaire_get_bucket_questionnaire_questions_uri(bucket_id=bucket_id,
                                                                 questionnaire_id=questionnaire_id))
    response = bc_api_get(uri=api_questionnaire_get_bucket_questionnaire_question, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    question_list = ""
    for question in data:

        # process question
        try:
            _question = BcQuestion.objects.get(id=question["id"])
        except BcQuestion.DoesNotExist:
            # save todolist only at app_todolist_detail
            _question = None

        _saved_on_db = " (db)" if _question else ""

        question_list += (f'<li><a href="' + reverse('app-question-detail',
                                                     kwargs={'bucket_id': bucket_id, 'question_id': question["id"]}) +
                          f'">{question["id"]}</a> {question["title"]} {_saved_on_db}</li>')

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

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

    # request to get message API
    api_questionnaire_get_bucket_question = (
        api_questionnaire_get_bucket_question_uri(bucket_id=bucket_id, question_id=question_id))
    response = bc_api_get(uri=api_questionnaire_get_bucket_question, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    question = response.json()

    if ('parent' in question and question["parent"]["type"] in ["Questionnaire"] and
            'bucket' in question and question["bucket"]["type"] == "Project" and
            'creator' in question and 'schedule' in question):

        if question["parent"]["type"] == "Questionnaire":
            # process parent BcQuestionnaire
            try:
                parent = BcQuestionnaire.objects.get(id=question["parent"]["id"])
            except BcQuestionnaire.DoesNotExist:
                # can not insert new Questionnaire with limited data of question["parent"]
                return HttpResponseBadRequest(
                    f'questionnaire not found: {question["parent"]}<br/>'
                    '<a href="' + reverse('app-questionnaire-detail',
                                          kwargs={'bucket_id': question["bucket"]["id"],
                                                  'questionnaire_id': question["parent"]["id"]}) +
                    '">try to open questionnaire</a> first.'
                )

        else:  # condition above has filter the type in to Questionnaire, should never be here
            parent = None

        # remove 'parent' key from question, will use model instance parent instead
        question.pop('parent')

        # process bucket
        try:
            bucket = BcProject.objects.get(id=question["bucket"]["id"])
        except BcProject.DoesNotExist:
            # can not insert new Project with limited data of question["bucket"]
            return HttpResponseBadRequest(
                f'bucket not found: {question["bucket"]}<br/>'
                '<a href="' + reverse('app-project-detail-update-db',
                                      kwargs={'project_id': question["bucket"]["id"]}) +
                '">save project to db</a> first.'
            )

        # remove 'bucket' key from question, will use model instance bucket instead
        question.pop('bucket')

        # process creator
        try:
            creator = BcPeople.objects.get(id=question["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=question["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

        # remove 'creator' key from question, will use model instance creator instead
        question.pop('creator')

        # process question and schedule (because schedule has no id, the only access via ForeignKey)

        try:
            _question = BcQuestion.objects.get(id=question["id"])
        except BcQuestion.DoesNotExist:

            json_days = json_dumps(question["schedule"]["days"])
            question["schedule"].pop('days')
            schedule = BcQuestionSchedule.objects.create(days=json_days, **question["schedule"])
            schedule.save()
            # remove 'schedule' key from question, will use model instance question instead
            question.pop('schedule')

            _question = BcQuestion.objects.create(parent=parent, bucket=bucket, creator=creator,
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

    # request to get message board API
    api_questionnaire_get_bucket_question_answer = (
        api_questionnaire_get_bucket_question_answers_uri(bucket_id=bucket_id, question_id=question_id))
    response = bc_api_get(uri=api_questionnaire_get_bucket_question_answer, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    answer_list = ""
    for answer in data:
        print(answer)
        print(answer.keys())

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

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

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

    # request to get message API
    api_questionnaire_get_bucket_question_answer = (
        api_questionnaire_get_bucket_question_answer_uri(bucket_id=bucket_id, question_answer_id=question_answer_id))
    response = bc_api_get(uri=api_questionnaire_get_bucket_question_answer, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    answer = response.json()
    print(answer)
    print(answer.keys())

    if ('parent' in answer and answer["parent"]["type"] in ["Question"] and
            'bucket' in answer and answer["bucket"]["type"] == "Project" and 'creator' in answer):

        if answer["parent"]["type"] == "Question":
            # process parent BcQuestion
            try:
                parent = BcQuestion.objects.get(id=answer["parent"]["id"])
            except BcQuestion.DoesNotExist:
                # can not insert new Question with limited data of answer["parent"]
                return HttpResponseBadRequest(
                    f'question not found: {answer["parent"]}<br/>'
                    '<a href="' + reverse('app-question-detail',
                                          kwargs={'bucket_id': answer["bucket"]["id"],
                                                  'question_id': answer["parent"]["id"]}) +
                    '">try to open question</a> first.'
                )

        else:  # condition above has filter the type in to Question, should never be here
            parent = None

        # remove 'parent' key from question, will use model instance parent instead
        answer.pop('parent')

        # process bucket
        try:
            bucket = BcProject.objects.get(id=answer["bucket"]["id"])
        except BcProject.DoesNotExist:
            # can not insert new Project with limited data of answer["bucket"]
            return HttpResponseBadRequest(
                f'bucket not found: {answer["bucket"]}<br/>'
                '<a href="' + reverse('app-project-detail-update-db',
                                      kwargs={'project_id': answer["bucket"]["id"]}) +
                '">save project to db</a> first.'
            )

        # remove 'bucket' key from answer, will use model instance bucket instead
        answer.pop('bucket')

        # process creator
        try:
            creator = BcPeople.objects.get(id=answer["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=answer["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

        # remove 'creator' key from question, will use model instance creator instead
        answer.pop('creator')

        # process question answer
        try:
            _question_answer = BcQuestionAnswer.objects.get(id=answer["id"])
        except BcQuestionAnswer.DoesNotExist:
            _question_answer = BcQuestionAnswer.objects.create(parent=parent, bucket=bucket, creator=creator, **answer)
            _question_answer.save()

    else:
        return HttpResponseBadRequest(
            f'answer {answer["title"]} has no creator or bucket type Project or parent type Question')

    _question_answer_title = _question_answer.title if _question_answer else answer["title"]

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_question_answer_title}<br/>'
        f'type: {answer["type"]}<br/>'
        f'comments_count: {answer["comments_count"]}<br/>'
    )
