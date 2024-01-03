from django.test import TestCase

from os import environ
from unittest.mock import patch

import bc.utils


class UtilsApiTest(TestCase):

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods
        environ["BASECAMP_API_URI"] = "https://3.basecampapi.com"
        environ["BASECAMP_ACCOUNT_ID"] = "1234567"
        environ["BASECAMP_USER_AGENT"] = "Intelligence (https://github.com/oonid/intelligence)"

    def setUp(self):  # Run once for every test method to set up clean data
        self.basecamp_api_uri = environ["BASECAMP_API_URI"]
        self.basecamp_account_id = environ["BASECAMP_ACCOUNT_ID"]  # id of the organization
        self.basecamp_user_agent = environ["BASECAMP_USER_AGENT"]
        self.base_uri = f'{self.basecamp_api_uri}/{self.basecamp_account_id}'

    def test_bc_api_get(self):
        uri = f'{self.base_uri}/my/profile.json'
        access_token = 'my access token'
        mock_response_status_ok = 200
        with patch('bc.utils.api.http_get') as mock_requests_get:
            mock_requests_get.return_value.status_code = mock_response_status_ok
            api_response = bc.utils.bc_api_get(uri=uri, access_token=access_token)
            mock_requests_get.assert_called_once()
            self.assertEqual(api_response.status_code, mock_response_status_ok)

    def test_api_message_get_bucket_message_types_uri(self):
        bucket_id = 1
        api_uri = bc.utils.api_message_get_bucket_message_types_uri(bucket_id=bucket_id)
        self.assertEqual(api_uri,
                         f'{self.base_uri}/buckets/{bucket_id}/categories.json')

    def test_api_message_get_bucket_message_board_uri(self):
        bucket_id = 1
        message_board_id = 2
        api_uri = bc.utils.api_message_get_bucket_message_board_uri(
            bucket_id=bucket_id, message_board_id=message_board_id)
        self.assertEqual(api_uri,
                         f'{self.base_uri}/buckets/{bucket_id}/message_boards/{message_board_id}.json')

    def test_api_message_get_bucket_message_board_messages_uri(self):
        bucket_id = 1
        message_board_id = 2
        api_uri = bc.utils.api_message_get_bucket_message_board_messages_uri(
            bucket_id=bucket_id, message_board_id=message_board_id)
        self.assertEqual(api_uri,
                         f'{self.base_uri}/buckets/{bucket_id}/message_boards/{message_board_id}/messages.json')

    def test_api_message_get_bucket_message_uri(self):
        bucket_id = 1
        message_id = 2
        api_uri = bc.utils.api_message_get_bucket_message_uri(bucket_id=bucket_id, message_id=message_id)
        self.assertEqual(api_uri,
                         f'{self.base_uri}/buckets/{bucket_id}/messages/{message_id}.json')

    def test_api_people_my_profile_uri(self):
        api_uri = bc.utils.api_people_my_profile_uri()
        self.assertEqual(api_uri, f'{self.base_uri}/my/profile.json')

    def test_api_people_get_person_uri(self):
        people_id = 1
        api_uri = bc.utils.api_people_get_person_uri(people_id=people_id)
        self.assertEqual(api_uri,
                         f'{self.base_uri}/people/{people_id}.json')

    def test_api_people_get_all_people_uri(self):
        api_uri = bc.utils.api_people_get_all_people_uri()
        self.assertEqual(api_uri, f'{self.base_uri}/people.json')

    def test_api_project_get_all_projects_uri(self):
        api_uri = bc.utils.api_project_get_all_projects_uri()
        self.assertEqual(api_uri, f'{self.base_uri}/projects.json')

    def test_api_project_get_project_uri(self):
        project_id = 1
        api_uri = bc.utils.api_project_get_project_uri(project_id=project_id)
        self.assertEqual(api_uri, f'{self.base_uri}/projects/{project_id}.json')

    def test_api_questionnaire_get_bucket_questionnaire_uri(self):
        bucket_id = 1
        questionnaire_id = 2
        api_uri = bc.utils.api_questionnaire_get_bucket_questionnaire_uri(
            bucket_id=bucket_id, questionnaire_id=questionnaire_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/questionnaires/{questionnaire_id}.json')

    def test_api_questionnaire_get_bucket_questionnaire_questions_uri(self):
        bucket_id = 1
        questionnaire_id = 2
        api_uri = bc.utils.api_questionnaire_get_bucket_questionnaire_questions_uri(
            bucket_id=bucket_id, questionnaire_id=questionnaire_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/questionnaires/{questionnaire_id}/'
                                  f'questions.json')

    def test_api_questionnaire_get_bucket_question_uri(self):
        bucket_id = 1
        question_id = 2
        api_uri = bc.utils.api_questionnaire_get_bucket_question_uri(bucket_id=bucket_id, question_id=question_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/questions/{question_id}.json')

    def test_api_questionnaire_get_bucket_question_answers_uri(self):
        bucket_id = 1
        question_id = 2
        api_uri = bc.utils.api_questionnaire_get_bucket_question_answers_uri(
            bucket_id=bucket_id, question_id=question_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/questions/{question_id}/answers.json')

    def test_api_questionnaire_get_bucket_question_answer_uri(self):
        bucket_id = 1
        question_answer_id = 2
        api_uri = bc.utils.api_questionnaire_get_bucket_question_answer_uri(
            bucket_id=bucket_id, question_answer_id=question_answer_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/question_answers/'
                                  f'{question_answer_id}.json')

    def test_api_schedule_get_bucket_schedule_uri(self):
        bucket_id = 1
        schedule_id = 2
        api_uri = bc.utils.api_schedule_get_bucket_schedule_uri(bucket_id=bucket_id, schedule_id=schedule_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/schedules/{schedule_id}.json')

    def test_api_schedule_get_bucket_schedule_entries_uri(self):
        bucket_id = 1
        schedule_id = 2
        api_uri = bc.utils.api_schedule_get_bucket_schedule_entries_uri(bucket_id=bucket_id, schedule_id=schedule_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/schedules/{schedule_id}/entries.json')

    def test_api_schedule_get_bucket_schedule_entry_uri(self):
        bucket_id = 1
        schedule_entry_id = 2
        api_uri = bc.utils.api_schedule_get_bucket_schedule_entry_uri(
            bucket_id=bucket_id, schedule_entry_id=schedule_entry_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/schedule_entries/'
                                  f'{schedule_entry_id}.json')

    def test_api_todoset_get_bucket_todoset_uri(self):
        bucket_id = 1
        todoset_id = 2
        api_uri = bc.utils.api_todoset_get_bucket_todoset_uri(bucket_id=bucket_id, todoset_id=todoset_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/todosets/{todoset_id}.json')

    def test_api_todolist_get_bucket_todoset_todolists_uri(self):
        bucket_id = 1
        todoset_id = 2
        api_uri = bc.utils.api_todolist_get_bucket_todoset_todolists_uri(bucket_id=bucket_id, todoset_id=todoset_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/todosets/{todoset_id}/todolists.json')

    def test_api_todolist_get_bucket_todolist_uri(self):
        bucket_id = 1
        todolist_id = 2
        api_uri = bc.utils.api_todolist_get_bucket_todolist_uri(bucket_id=bucket_id, todolist_id=todolist_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/todolists/{todolist_id}.json')

    def test_api_todolist_group_get_todolist_groups_uri(self):
        bucket_id = 1
        todolist_id = 2
        api_uri = bc.utils.api_todolist_group_get_todolist_groups_uri(bucket_id=bucket_id, todolist_id=todolist_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/todolists/{todolist_id}/groups.json')

    def test_api_todo_get_bucket_todolist_todos_uri(self):
        bucket_id = 1
        todolist_id = 2
        api_uri = bc.utils.api_todo_get_bucket_todolist_todos_uri(bucket_id=bucket_id, todolist_id=todolist_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/todolists/{todolist_id}/todos.json')

    def test_api_todo_get_bucket_todo_uri(self):
        bucket_id = 1
        todo_id = 2
        api_uri = bc.utils.api_todo_get_bucket_todo_uri(bucket_id=bucket_id, todo_id=todo_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/todos/{todo_id}.json')

    def test_api_recording_get_recordings_uri(self):
        recording_type = 'Todo'
        bucket = 1
        api_uri = bc.utils.api_recording_get_recordings_uri(recording_type=recording_type, bucket=bucket)
        self.assertEqual(api_uri,
                         f'{self.base_uri}/projects/recordings.json?type={recording_type}&bucket={bucket}')

    def test_api_recording_get_recordings_uri_with_invalid_recording_type(self):
        recording_type = 'Cloud'  # invalid, undefined in static_get_recording_types()
        bucket = 1
        try:
            api_uri = bc.utils.api_recording_get_recordings_uri(recording_type=recording_type, bucket=bucket)
        except ValueError as e:
            self.assertEqual(str(e), 'undefined recording_type')

    def test_api_recording_get_bucket_recording_parent_comment_uri(self):
        bucket_id = 1
        parent_id = 2
        api_uri = bc.utils.api_recording_get_bucket_recording_parent_comment_uri(
            bucket_id=bucket_id, parent_id=parent_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/recordings/{parent_id}/comments.json')

    def test_api_comment_get_bucket_comment_uri(self):
        bucket_id = 1
        comment_id = 2
        api_uri = bc.utils.api_comment_get_bucket_comment_uri(bucket_id=bucket_id, comment_id=comment_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/comments/{comment_id}.json')

    def test_api_vault_get_bucket_vault_uri(self):
        bucket_id = 1
        vault_id = 2
        api_uri = bc.utils.api_vault_get_bucket_vault_uri(bucket_id=bucket_id, vault_id=vault_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/vaults/{vault_id}.json')

    def test_api_vault_get_bucket_vault_vaults_uri(self):
        bucket_id = 1
        vault_id = 2
        api_uri = bc.utils.api_vault_get_bucket_vault_vaults_uri(bucket_id=bucket_id, vault_id=vault_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/vaults/{vault_id}/vaults.json')

    def test_api_vault_get_bucket_vault_documents_uri(self):
        bucket_id = 1
        vault_id = 2
        api_uri = bc.utils.api_vault_get_bucket_vault_documents_uri(bucket_id=bucket_id, vault_id=vault_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/vaults/{vault_id}/documents.json')

    def test_api_vault_get_bucket_vault_uploads_uri(self):
        bucket_id = 1
        vault_id = 2
        api_uri = bc.utils.api_vault_get_bucket_vault_uploads_uri(bucket_id=bucket_id, vault_id=vault_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/vaults/{vault_id}/uploads.json')

    def test_api_document_get_bucket_document_uri(self):
        bucket_id = 1
        document_id = 2
        api_uri = bc.utils.api_document_get_bucket_document_uri(bucket_id=bucket_id, document_id=document_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/documents/{document_id}.json')

    def test_api_document_get_bucket_upload_uri(self):
        bucket_id = 1
        upload_id = 2
        api_uri = bc.utils.api_document_get_bucket_upload_uri(bucket_id=bucket_id, upload_id=upload_id)
        self.assertEqual(api_uri, f'{self.base_uri}/buckets/{bucket_id}/uploads/{upload_id}.json')