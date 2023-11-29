from django.urls import reverse
from bc.models import BcProject, BcTodo, BcTodolist, BcScheduleEntry, BcQuestionAnswer, BcMessage, BcVault
from bc.utils import static_get_comment_parent_types, static_get_vault_parent_types


def db_get_bucket(bucket_id):
    try:
        _bucket = BcProject.objects.get(id=bucket_id)
        _message = None
    except BcProject.DoesNotExist:
        _bucket = None
        _message = (f'bucket {bucket_id} not found<br/>'
                    f'<a href="' + reverse('app-project-detail-update-db',
                                           kwargs={'project_id': bucket_id}) +
                    '">save project to db</a> first.')

    return _bucket, _message


def db_get_comment_parent(parent, bucket_id):
    """
    as mention in static_get_comment_parent_types(), parent types should be in
    ['Message', 'Question::Answer', 'Schedule::Entry', 'Todolist', 'Todo']
    :param parent:
    :param bucket_id:
    :return:
    """

    if parent['type'] == 'Todo':
        # process parent BcTodo
        try:
            _parent = BcTodo.objects.get(id=parent["id"])
            _message = None
        except BcTodo.DoesNotExist:
            _parent = None
            _message = (f'todo {parent["id"]} not found<br/>'
                        '<a href="' + reverse('app-todo-detail',
                                              kwargs={'bucket_id': bucket_id,
                                                      'todo_id': parent["id"]}) +
                        '">try to open todo</a> first.')

    elif parent['type'] == 'Todolist':
        # process parent BcTodolist
        try:
            _parent = BcTodolist.objects.get(id=parent["id"])
            _message = None
        except BcTodolist.DoesNotExist:
            _parent = None
            _message = (f'todolist {parent["id"]} not found<br/>'
                        '<a href="' + reverse('app-todolist-detail',
                                              kwargs={'bucket_id': bucket_id,
                                                      'todolist_id': parent["id"]}) +
                        '">try to open todolist</a> first.')

    elif parent['type'] == 'Schedule::Entry':
        # process parent BcScheduleEntry
        try:
            _parent = BcScheduleEntry.objects.get(id=parent["id"])
            _message = None
        except BcScheduleEntry.DoesNotExist:
            _parent = None
            _message = (f'schedule entry {parent["id"]} not found<br/>'
                        '<a href="' + reverse('app-schedule-entry-detail',
                                              kwargs={'bucket_id': bucket_id,
                                                      'schedule_entry_id': parent["id"]}) +
                        '">try to open schedule entry</a> first.')

    elif parent['type'] == 'Question::Answer':
        # process parent BcQuestionAnswer
        try:
            _parent = BcQuestionAnswer.objects.get(id=parent["id"])
            _message = None
        except BcQuestionAnswer.DoesNotExist:
            _parent = None
            _message = (f'question answer {parent["id"]} not found<br/>'
                        '<a href="' + reverse('app-question-answer-detail',
                                              kwargs={'bucket_id': bucket_id,
                                                      'question_answer_id': parent["id"]}) +
                        '">try to open question answer</a> first.')

    elif parent['type'] == 'Message':
        # process parent BcMessage
        try:
            _parent = BcMessage.objects.get(id=parent["id"])
            _message = None
        except BcMessage.DoesNotExist:
            _parent = None
            _message = (f'message {parent["id"]} not found<br/>'
                        '<a href="' + reverse('app-message-detail',
                                              kwargs={'bucket_id': bucket_id,
                                                      'message_id': parent["id"]}) +
                        '">try to open message</a> first.')

    else:  # condition above has filter the type in to get_recording_parent_types, should never be here
        _parent = None
        _message = f'parent {parent["id"]} type {parent["type"]} not in {static_get_comment_parent_types()}.'

    return _parent, _message


def db_get_vault_parent(parent, bucket_id):
    """
    as mention in static_get_vault_parent_types(), parent types should be in ['Vault']

    :param parent:
    :param bucket_id:
    :return:
    """

    if parent['type'] == 'Vault':
        # process parent BcVault
        try:
            _parent = BcVault.objects.get(id=parent["id"])
            _message = None
        except BcVault.DoesNotExist:
            _parent = None
            _message = (f'vault {parent["id"]} not found<br/>'
                        '<a href="' + reverse('app-vault-detail',
                                              kwargs={'bucket_id': bucket_id,
                                                      'vault_id': parent["id"]}) +
                        '">try to open vault</a> first.')

    else:  # condition above has filter the type in to get_vault_parent_types, should never be here
        _parent = None
        _message = f'parent {parent["id"]} type {parent["type"]} not in {static_get_vault_parent_types()}.'

    return _parent, _message
