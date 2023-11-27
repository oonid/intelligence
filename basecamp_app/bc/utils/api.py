from os import environ
from requests import get as http_get

# utilities to process environment variables and APIs


def bc_api_get(uri, access_token):
    basecamp_user_agent = environ["BASECAMP_USER_AGENT"]
    return http_get(url=uri,
                    headers={"Authorization": "Bearer " + access_token, "User-Agent": basecamp_user_agent})


def api_message_get_bucket_message_types_uri(bucket_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/categories.json'


def api_message_get_bucket_message_board_uri(bucket_id, message_board_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/message_boards/{message_board_id}.json'


def api_message_get_bucket_message_board_messages_uri(bucket_id, message_board_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return (f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/message_boards/{message_board_id}/'
            f'messages.json')


def api_message_get_bucket_message_uri(bucket_id, message_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/messages/{message_id}.json'


def api_people_my_profile_uri():
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/my/profile.json'


def api_people_get_person_uri(people_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/people/{people_id}.json'


def api_people_get_all_people_uri():
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/people.json'


def api_project_get_all_projects_uri():
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/projects.json'


def api_project_get_project_uri(project_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/projects/{project_id}.json'


def api_questionnaire_get_bucket_questionnaire_uri(bucket_id, questionnaire_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/questionnaires/{questionnaire_id}.json'


def api_questionnaire_get_bucket_questionnaire_questions_uri(bucket_id, questionnaire_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return (f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/questionnaires/{questionnaire_id}/'
            f'questions.json')


def api_questionnaire_get_bucket_question_uri(bucket_id, question_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/questions/{question_id}.json'


def api_questionnaire_get_bucket_question_answers_uri(bucket_id, question_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/questions/{question_id}/answers.json'


def api_questionnaire_get_bucket_question_answer_uri(bucket_id, question_answer_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/question_answers/{question_answer_id}.json'


def api_schedule_get_bucket_schedule_uri(bucket_id, schedule_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/schedules/{schedule_id}.json'


def api_schedule_get_bucket_schedule_entries_uri(bucket_id, schedule_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/schedules/{schedule_id}/entries.json'


def api_schedule_get_bucket_schedule_entry_uri(bucket_id, schedule_entry_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/schedule_entries/{schedule_entry_id}.json'


def api_todoset_get_bucket_todoset_uri(bucket_id, todoset_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/todosets/{todoset_id}.json'


def api_todolist_get_bucket_todoset_todolists_uri(bucket_id, todoset_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/todosets/{todoset_id}/todolists.json'


def api_todolist_get_bucket_todolist_uri(bucket_id, todolist_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/todolists/{todolist_id}.json'


def api_todolist_group_get_todolist_groups_uri(bucket_id, todolist_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/todolists/{todolist_id}/groups.json'


def api_todo_get_bucket_todolist_todos_uri(bucket_id, todolist_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/todolists/{todolist_id}/todos.json'


def api_todo_get_bucket_todo_uri(bucket_id, todo_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/todos/{todo_id}.json'


def api_recording_get_recordings_uri(recording_type, bucket=None):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/recordings.md#get-recordings
    :param recording_type: Required parameters.
        which must be Comment, Document, Message, Question::Answer, Schedule::Entry, Todo, Todolist, Upload, or Vault.
    :param bucket: Single/comma separated list of project IDs. Default: All active projects visible to the current user.
    :return:
    """
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    if not recording_type:  # undefined recording_type
        raise ValueError('undefined recording_type')
    # recording_type defined
    api_uri = f'{basecamp_api_uri}/{basecamp_account_id}/projects/recordings.json?type={recording_type}'

    if bucket:  # defined bucket
        api_uri += f'&bucket={bucket}'

    return api_uri


def api_recording_get_bucket_recording_parent_comment_uri(bucket_id, parent_id):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/comments.md#get-comments
    the documentation said the ID is recording ID, but the API always response with empty list [].
    replace the ID with parent ID and the response as expected, list of comments.
    :param bucket_id:
    :param parent_id:
    :return:
    """
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/recordings/{parent_id}/comments.json'


def api_comment_get_bucket_comment_uri(bucket_id, comment_id):
    basecamp_api_uri = environ["BASECAMP_API_URI"]
    basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
    return f'{basecamp_api_uri}/{basecamp_account_id}/buckets/{bucket_id}/comments/{comment_id}.json'
