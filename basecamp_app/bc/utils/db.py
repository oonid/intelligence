from django.urls import reverse

from bc.models import (BcProject, BcPeople, BcTodo, BcTodolist, BcScheduleEntry, BcQuestionAnswer, BcMessage,
                       BcMessageBoard, BcVault, BcUpload, BcDocument)
from bc.serializers import BcPeopleSerializer
from bc.utils import (repr_message_detail_not_found,
                      static_get_comment_parent_types, static_get_message_parent_types, static_get_vault_parent_types)


def db_get_bucket(bucket_id):
    try:
        _bucket = BcProject.objects.get(id=bucket_id)
        _exception = None
    except BcProject.DoesNotExist:
        _bucket = None
        _exception = (f'bucket {bucket_id} not found<br/>'
                      f'<a href="' + reverse('app-project-detail-update-db',
                                             kwargs={'project_id': bucket_id}) +
                      '">save project to db</a> first.')

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
            _exception = f'creator serializer error: {serializer.errors}'

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
        _exception = f'invalid message type {_message_type}.'

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
            _exception = (f'upload {parent["id"]} not found<br/>'
                          '<a href="' + reverse('app-upload-detail',
                                                kwargs={'bucket_id': bucket_id, 'upload_id': parent["id"]}) +
                          '">try to open upload</a> first.')

    elif parent['type'] == 'Todo':
        # process parent BcTodo
        try:
            _parent = BcTodo.objects.get(id=parent["id"])
            _exception = None
        except BcTodo.DoesNotExist:
            _parent = None
            _exception = (f'todo {parent["id"]} not found<br/>'
                          '<a href="' + reverse('app-todo-detail',
                                                kwargs={'bucket_id': bucket_id, 'todo_id': parent["id"]}) +
                          '">try to open todo</a> first.')

    elif parent['type'] == 'Todolist':
        # process parent BcTodolist
        try:
            _parent = BcTodolist.objects.get(id=parent["id"])
            _exception = None
        except BcTodolist.DoesNotExist:
            _parent = None
            _exception = (f'todolist {parent["id"]} not found<br/>'
                          '<a href="' + reverse('app-todolist-detail',
                                                kwargs={'bucket_id': bucket_id, 'todolist_id': parent["id"]}) +
                          '">try to open todolist</a> first.')

    elif parent['type'] == 'Schedule::Entry':
        # process parent BcScheduleEntry
        try:
            _parent = BcScheduleEntry.objects.get(id=parent["id"])
            _exception = None
        except BcScheduleEntry.DoesNotExist:
            _parent = None
            _exception = (f'schedule entry {parent["id"]} not found<br/>'
                          '<a href="' + reverse('app-schedule-entry-detail',
                                                kwargs={'bucket_id': bucket_id, 'schedule_entry_id': parent["id"]}) +
                          '">try to open schedule entry</a> first.')

    elif parent['type'] == 'Question::Answer':
        # process parent BcQuestionAnswer
        try:
            _parent = BcQuestionAnswer.objects.get(id=parent["id"])
            _exception = None
        except BcQuestionAnswer.DoesNotExist:
            _parent = None
            _exception = (f'question answer {parent["id"]} not found<br/>'
                          '<a href="' + reverse('app-question-answer-detail',
                                                kwargs={'bucket_id': bucket_id, 'question_answer_id': parent["id"]}) +
                          '">try to open question answer</a> first.')

    elif parent['type'] == 'Message':
        # process parent BcMessage
        try:
            _parent = BcMessage.objects.get(id=parent["id"])
            _exception = None
        except BcMessage.DoesNotExist:
            _parent = None
            _exception = repr_message_detail_not_found(message=parent, bucket_id=bucket_id)

    elif parent['type'] == 'Document':
        # process parent BcDocument
        try:
            _parent = BcDocument.objects.get(id=parent["id"])
            _exception = None
        except BcDocument.DoesNotExist:
            _parent = None
            _exception = (f'document {parent["id"]} not found<br/>'
                          '<a href="' + reverse('app-document-detail',
                                                kwargs={'bucket_id': bucket_id, 'document_id': parent["id"]}) +
                          '">try to open document</a> first.')

    else:  # condition above has filter the type in to get_recording_parent_types, should never be here
        _parent = None
        _exception = f'parent {parent["id"]} type {parent["type"]} not in {static_get_comment_parent_types()}.'

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
            _exception = (f'message board {parent["id"]} not found<br/>'
                          '<a href="' + reverse('app-message-board-detail',
                                                kwargs={'bucket_id': bucket_id,
                                                        'message_board_id': parent["id"]}) +
                          '">try to open message board</a> first.')

    else:  # condition above has filter the type in to get_vault_parent_types, should never be here
        _parent = None
        _exception = f'parent {parent["id"]} type {parent["type"]} not in {static_get_message_parent_types()}.'

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
            _exception = (f'vault {parent["id"]} not found<br/>'
                          '<a href="' + reverse('app-vault-detail',
                                                kwargs={'bucket_id': bucket_id, 'vault_id': parent["id"]}) +
                          '">try to open vault</a> first.')

    else:  # condition above has filter the type in to get_vault_parent_types, should never be here
        _parent = None
        _exception = f'parent {parent["id"]} type {parent["type"]} not in {static_get_vault_parent_types()}.'

    return _parent, _exception
