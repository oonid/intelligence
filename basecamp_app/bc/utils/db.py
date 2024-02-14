from django.urls import reverse

from bc.models import (BcProject, BcPeople, BcTodo, BcTodolist, BcScheduleEntry, BcQuestionAnswer, BcMessage,
                       BcMessageBoard, BcVault, BcUpload, BcDocument)
from bc.serializers import BcPeopleSerializer
from bc.utils import (repr_message_detail_not_found, repr_http_response_template_string,
                      repr_template_response_parent_not_in_list, repr_template_response_entity_not_found,
                      static_get_comment_parent_types, static_get_message_parent_types, static_get_vault_parent_types)


def db_get_bucket(bucket_id):
    try:
        _bucket = BcProject.objects.get(id=bucket_id)
        _exception = None
    except BcProject.DoesNotExist:
        _bucket = None
        template_str = 'bucket {{ bucket_id }} not found<br/><a href="{{ href }}">save project to db</a> first.'
        context_dict = {'bucket_id': bucket_id,
                        'href': reverse('app-project-detail-update-db', kwargs={'project_id': bucket_id})}
        _exception = repr_http_response_template_string(template_str=template_str, context_dict=context_dict)

    return _bucket, _exception


def db_get_or_create_person(person):
    try:
        _exception = None  # assign _exception above _recording to comply the coverage :)
        _creator = BcPeople.objects.get(id=person["id"])
    except BcPeople.DoesNotExist:
        serializer = BcPeopleSerializer(data=person)
        if serializer.is_valid():
            _creator = serializer.save()
            _exception = None
        else:  # invalid serializer
            _creator = None
            template_str = 'creator serializer error: {{ serializer_errors }}'
            context_dict = {'serializer_errors': serializer.errors}
            _exception = repr_http_response_template_string(template_str=template_str, context_dict=context_dict)

    return _creator, _exception


def db_get_message(message, bucket_id):
    if 'type' in message and message["type"] == 'Message':
        try:
            _message = BcMessage.objects.get(id=message["id"])
            _exception = None
        except BcMessage.DoesNotExist:
            _message = None
            _exception = repr_message_detail_not_found(message=message, bucket_id=bucket_id)

    else:  # invalid message type
        _message = None
        _message_type = f'({message["type"]})' if 'type' in message else ''
        template_str = 'invalid message type {{ message_type }}.'
        context_dict = {'message_type': _message_type}
        _exception = repr_http_response_template_string(template_str=template_str, context_dict=context_dict)

    return _message, _exception


def db_get_comment_parent(parent, bucket_id):
    """
    as mentioned in static_get_comment_parent_types()

    :param parent:
    :param bucket_id:
    :return:
    """

    if parent['type'] == 'Upload':
        # process parent BcUpload
        try:
            _parent = BcUpload.objects.get(id=parent["id"])
            _exception = None
        except BcUpload.DoesNotExist:
            _parent = None
            _exception = repr_template_response_entity_not_found(
                entity_id=parent["id"], entity_type=parent["type"],
                href=reverse('app-upload-detail', kwargs={'bucket_id': bucket_id, 'upload_id': parent["id"]}))

    elif parent['type'] == 'Todo':
        # process parent BcTodo
        try:
            _parent = BcTodo.objects.get(id=parent["id"])
            _exception = None
        except BcTodo.DoesNotExist:
            _parent = None
            _exception = repr_template_response_entity_not_found(
                entity_id=parent["id"], entity_type=parent["type"],
                href=reverse('app-todo-detail', kwargs={'bucket_id': bucket_id, 'todo_id': parent["id"]}))

    elif parent['type'] == 'Todolist':
        # process parent BcTodolist
        try:
            _parent = BcTodolist.objects.get(id=parent["id"])
            _exception = None
        except BcTodolist.DoesNotExist:
            _parent = None
            _exception = repr_template_response_entity_not_found(
                entity_id=parent["id"], entity_type=parent["type"],
                href=reverse('app-todolist-detail', kwargs={'bucket_id': bucket_id, 'todolist_id': parent["id"]}))

    elif parent['type'] == 'Schedule::Entry':
        # process parent BcScheduleEntry
        try:
            _parent = BcScheduleEntry.objects.get(id=parent["id"])
            _exception = None
        except BcScheduleEntry.DoesNotExist:
            _parent = None
            _exception = repr_template_response_entity_not_found(
                entity_id=parent["id"], entity_type=parent["type"],
                href=reverse('app-schedule-entry-detail',
                             kwargs={'bucket_id': bucket_id, 'schedule_entry_id': parent["id"]}))

    elif parent['type'] == 'Question::Answer':
        # process parent BcQuestionAnswer
        try:
            _parent = BcQuestionAnswer.objects.get(id=parent["id"])
            _exception = None
        except BcQuestionAnswer.DoesNotExist:
            _parent = None
            _exception = repr_template_response_entity_not_found(
                entity_id=parent["id"], entity_type=parent["type"],
                href=reverse('app-question-answer-detail',
                             kwargs={'bucket_id': bucket_id, 'question_answer_id': parent["id"]}))

    elif parent['type'] == 'Message':
        # process parent BcMessage
        try:
            _parent = BcMessage.objects.get(id=parent["id"])
            _exception = None
        except BcMessage.DoesNotExist:
            _parent = None
            _exception = repr_template_response_entity_not_found(
                entity_id=parent["id"], entity_type=parent["type"],
                href=reverse('app-message-detail', kwargs={'bucket_id': bucket_id, 'message_id': parent["id"]}))

    elif parent['type'] == 'Document':
        # process parent BcDocument
        try:
            _parent = BcDocument.objects.get(id=parent["id"])
            _exception = None
        except BcDocument.DoesNotExist:
            _parent = None
            _exception = repr_template_response_entity_not_found(
                entity_id=parent["id"], entity_type=parent["type"],
                href=reverse('app-document-detail', kwargs={'bucket_id': bucket_id, 'document_id': parent["id"]}))

    else:  # condition above has filter the type in to get_recording_parent_types, should never be here
        _parent = None
        _exception = repr_template_response_parent_not_in_list(parent_id=parent["id"], parent_type=parent["type"],
                                                               list_parent_types=static_get_comment_parent_types())

    return _parent, _exception


def db_get_message_parent(parent, bucket_id):
    """
    as mentioned in static_get_message_parent_types()

    :param parent:
    :param bucket_id:
    :return:
    """

    if parent['type'] == 'Message::Board':
        # process parent BcMessageBoard
        try:
            _parent = BcMessageBoard.objects.get(id=parent["id"])
            _exception = None
        except BcMessageBoard.DoesNotExist:
            _parent = None
            _exception = repr_template_response_entity_not_found(
                entity_id=parent["id"], entity_type=parent["type"],
                href=reverse('app-message-board-detail',
                             kwargs={'bucket_id': bucket_id, 'message_board_id': parent["id"]}))

    else:  # condition above has filter the type in to get_vault_parent_types, should never be here
        _parent = None
        _exception = repr_template_response_parent_not_in_list(
            parent_id=parent["id"], parent_type=parent["type"], list_parent_types=static_get_message_parent_types())

    return _parent, _exception


def db_get_vault_parent(parent, bucket_id):
    """
    as mentioned in static_get_vault_parent_types()

    :param parent:
    :param bucket_id:
    :return:
    """

    if parent['type'] == 'Vault':
        # process parent BcVault
        try:
            _parent = BcVault.objects.get(id=parent["id"])
            _exception = None
        except BcVault.DoesNotExist:
            _parent = None
            _exception = repr_template_response_entity_not_found(
                entity_id=parent["id"], entity_type=parent["type"],
                href=reverse('app-vault-detail', kwargs={'bucket_id': bucket_id, 'vault_id': parent["id"]}))

    else:  # condition above has filter the type in to get_vault_parent_types, should never be here
        _parent = None
        _exception = repr_template_response_parent_not_in_list(
            parent_id=parent["id"], parent_type=parent["type"], list_parent_types=static_get_vault_parent_types())

    return _parent, _exception
