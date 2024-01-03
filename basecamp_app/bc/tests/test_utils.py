from django.test import TestCase

from os import environ
from unittest.mock import patch
from pathlib import Path
from json import loads as json_loads, dumps as json_dumps, load as json_stream_load

import bc.utils


class UtilsDbTest(TestCase):
    fixtures = ["bc_bccompany", "bc_bcpeople",
                "bc_bcproject", "bc_bcprojecttool",
                "bc_bcquestionnaire", "bc_bcquestion", "bc_bcquestionanswer", "bc_bcrecurrenceschedule",
                "bc_bcschedule", "bc_bcscheduleentry",
                "bc_bcmessagecategory", "bc_bcmessageboard", "bc_bcmessage",
                "bc_bctodoset", "bc_bctodolist", "bc_bctodo", "bc_bctodocompletion",
                "bc_bcvault", "bc_bcdocument", "bc_bcupload",
                "bc_bccomment",]

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods

        # api_sample.json is collections of API data from bc3-api site https://github.com/basecamp/bc3-api/tree/master
        test_dir = Path(__file__).resolve().parent
        with open(test_dir / "api_sample.json") as stream:
            api_sample_json = json_stream_load(stream)

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/people.md
        # the database loaded with fixture bc_bcpeople.json and bc_bccompany.json
        cls.person_data = json_dumps(api_sample_json["person"]["1049715914"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md#get-a-message
        # the database loaded with fixture bc_bcmessage.json
        cls.message_data = json_dumps(api_sample_json["message"]["1069479351"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/comments.md#get-a-comment
        # the database loaded with fixture bc_bccomment.json
        cls.comment_data = json_dumps(api_sample_json["comment"]["1069479361"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/documents.md
        # the database loaded with fixture bc_bcdocument.json
        cls.document_data = json_dumps(api_sample_json["document"]["1069479093"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/uploads.md#get-an-upload
        # the database loaded with fixture bc_bcupload.json
        cls.upload_data = json_dumps(api_sample_json["upload"]["1069479848"])

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/todolists.md#example-json-response
        # the database loaded with fixture bc_bctodolist.json
        cls.todolist_data = json_dumps(api_sample_json["todolist"]["1069479520"])

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/todos.md#get-a-to-do
        # the database loaded with fixture bc_bctodo.json
        cls.todo_data = json_dumps(api_sample_json["todo"]["1069479523"])

        # sample from https://github.com/basecamp/bc3-api/blob/master/sections/schedule_entries.md#get-a-schedule-entry
        # the database loaded with fixture bc_bcscheduleentry.json
        cls.schedule_entry_data = json_dumps(api_sample_json["schedule_entry"]["1069479847"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/question_answers.md
        # the database loaded with fixture bc_bcquestionanswer.json
        cls.question_answer_data = json_dumps(api_sample_json["question_answer"]["1069479547"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/vaults.md#get-a-vault
        # using vault with ID 1069479340, generated as dummy data
        # the database loaded with fixture bc_bcvault.json
        cls.vault_1069479340_data = json_dumps(api_sample_json["vault"]["1069479340"])

    def setUp(self):  # Run once for every test method to set up clean data
        self.person = json_loads(self.person_data)
        self.message = json_loads(self.message_data, strict=False)  # disable strict to process content with \n
        self.comment = json_loads(self.comment_data)
        self.document = json_loads(self.document_data, strict=False)  # disable strict to process content with \n
        self.upload = json_loads(self.upload_data)
        self.todolist = json_loads(self.todolist_data)
        self.todo = json_loads(self.todo_data)
        self.schedule_entry = json_loads(self.schedule_entry_data)
        self.question_answer = json_loads(self.question_answer_data)
        self.vault = json_loads(self.vault_1069479340_data)

    def test_db_get_bucket(self):
        bucket_id = 2085958499
        _bucket, _exception = bc.utils.db_get_bucket(bucket_id=bucket_id)
        self.assertEqual(_exception, None)
        self.assertEqual(_bucket.id, bucket_id)

    def test_db_get_bucket_with_not_exist_bucket(self):
        bucket_id = 1
        _bucket, _exception = bc.utils.db_get_bucket(bucket_id=bucket_id)
        self.assertEqual(_exception, f'bucket {bucket_id} not found<br/><a href="/bc/project/1/update-db">'
                                     f'save project to db</a> first.')
        self.assertEqual(_bucket, None)

    def test_db_get_or_create_person(self):
        _creator, _exception = bc.utils.db_get_or_create_person(person=self.person)
        self.assertEqual(_exception, None)
        self.assertEqual(_creator.id, self.person["id"])

    def test_db_get_or_create_person_with_new_person(self):
        # change the person ID to new (non-exist) ID, as it also check by email address, change it too
        self.person["id"] = 1
        self.person["email_address"] = 'new@email.address'

        _creator, _exception = bc.utils.db_get_or_create_person(person=self.person)
        self.assertEqual(_exception, None)
        self.assertEqual(_creator.id, self.person["id"])

    def test_db_get_or_create_person_with_new_person_no_company(self):
        # remove company field from existing person data, and change the person ID to new (non-exist) ID
        self.person["id"] = 1
        self.person.pop('company')

        _creator, _exception = bc.utils.db_get_or_create_person(person=self.person)
        self.assertEqual(_exception, "creator serializer error: {'people company error': "
                                     "ErrorDetail(string='people no company field', code='invalid')}")
        self.assertEqual(_creator, None)

    def test_db_get_message(self):
        _message, _exception = bc.utils.db_get_message(message=self.message, bucket_id=self.message["bucket"]["id"])
        self.assertEqual(_exception, None)
        self.assertEqual(_message.id, self.message["id"])

    def test_db_get_message_with_invalid_message_type(self):
        # change message type to invalid type "Cloud"
        self.message["type"] = "Cloud"

        _message, _exception = bc.utils.db_get_message(message=self.message, bucket_id=self.message["bucket"]["id"])
        self.assertEqual(_exception, f'invalid message type ({self.message["type"]}).')
        self.assertEqual(_message, None)

    def test_db_get_message_with_new_message(self):
        # change message ID to new (non-exist) ID
        self.message["id"] = 1

        _message, _exception = bc.utils.db_get_message(message=self.message, bucket_id=self.message["bucket"]["id"])
        self.assertEqual(_exception, f'Message {self.message["id"]} not found<br/>'
                                     f'<a href="/bc/project/{self.message["bucket"]["id"]}/'
                                     f'message/{self.message["id"]}">try to open Message</a> first.')
        self.assertEqual(_message, None)

    def test_db_get_comment_parent_with_parent_type_message(self):
        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, None)
        self.assertEqual(_parent.id, self.comment["parent"]["id"])

    def test_db_get_comment_parent_with_parent_type_message_new_message(self):
        # change parent (message) ID to new (non-exist) ID
        self.comment["parent"]["id"] = 1

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, f'Message {self.comment["parent"]["id"]} not found<br/>'
                                     f'<a href="/bc/project/{self.comment["bucket"]["id"]}/'
                                     f'message/{self.comment["parent"]["id"]}">try to open Message</a> first.')
        self.assertEqual(_parent, None)

    def test_db_get_comment_parent_with_invalid_parent_type(self):
        # change parent type to invalid type "Cloud"
        self.comment["parent"]["type"] = "Cloud"

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, f'parent {self.comment["parent"]["id"]} type {self.comment["parent"]["type"]} not '
                                     f'in {bc.utils.static_get_comment_parent_types()}.')
        self.assertEqual(_parent, None)

    def test_db_get_comment_parent_with_parent_type_document(self):
        # change parent type to existing document
        self.comment["parent"]["type"] = self.document["type"]
        self.comment["parent"]["id"] = self.document["id"]

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, None)
        self.assertEqual(_parent.id, self.comment["parent"]["id"])

    def test_db_get_comment_parent_with_parent_type_document_new_document(self):
        # change parent (document) ID to new (non-exist) ID
        self.comment["parent"]["type"] = self.document["type"]
        self.comment["parent"]["id"] = 1

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, f'document {self.comment["parent"]["id"]} not found<br/>'
                                     f'<a href="/bc/project/{self.comment["bucket"]["id"]}/'
                                     f'document/{self.comment["parent"]["id"]}">try to open document</a> first.')
        self.assertEqual(_parent, None)

    def test_db_get_comment_parent_with_parent_type_upload(self):
        # change parent type to existing upload
        self.comment["parent"]["type"] = self.upload["type"]
        self.comment["parent"]["id"] = self.upload["id"]

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, None)
        self.assertEqual(_parent.id, self.comment["parent"]["id"])

    def test_db_get_comment_parent_with_parent_type_upload_new_upload(self):
        # change parent (upload) ID to new (non-exist) ID
        self.comment["parent"]["type"] = self.upload["type"]
        self.comment["parent"]["id"] = 1

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, f'upload {self.comment["parent"]["id"]} not found<br/>'
                                     f'<a href="/bc/project/{self.comment["bucket"]["id"]}/'
                                     f'upload/{self.comment["parent"]["id"]}">try to open upload</a> first.')
        self.assertEqual(_parent, None)

    def test_db_get_comment_parent_with_parent_type_todolist(self):
        # change parent type to existing todolist
        self.comment["parent"]["type"] = self.todolist["type"]
        self.comment["parent"]["id"] = self.todolist["id"]

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, None)
        self.assertEqual(_parent.id, self.comment["parent"]["id"])

    def test_db_get_comment_parent_with_parent_type_todolist_new_todolist(self):
        # change parent (todolist) ID to new (non-exist) ID
        self.comment["parent"]["type"] = self.todolist["type"]
        self.comment["parent"]["id"] = 1

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, f'todolist {self.comment["parent"]["id"]} not found<br/>'
                                     f'<a href="/bc/project/{self.comment["bucket"]["id"]}/'
                                     f'todolist/{self.comment["parent"]["id"]}">try to open todolist</a> first.')
        self.assertEqual(_parent, None)

    def test_db_get_comment_parent_with_parent_type_todo(self):
        # change parent type to existing todo
        self.comment["parent"]["type"] = self.todo["type"]
        self.comment["parent"]["id"] = self.todo["id"]

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, None)
        self.assertEqual(_parent.id, self.comment["parent"]["id"])

    def test_db_get_comment_parent_with_parent_type_todo_new_todo(self):
        # change parent (todo) ID to new (non-exist) ID
        self.comment["parent"]["type"] = self.todo["type"]
        self.comment["parent"]["id"] = 1

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, f'todo {self.comment["parent"]["id"]} not found<br/>'
                                     f'<a href="/bc/project/{self.comment["bucket"]["id"]}/'
                                     f'todo/{self.comment["parent"]["id"]}">try to open todo</a> first.')
        self.assertEqual(_parent, None)

    def test_db_get_comment_parent_with_parent_type_schedule_entry(self):
        # change parent type to existing schedule_entry
        self.comment["parent"]["type"] = self.schedule_entry["type"]
        self.comment["parent"]["id"] = self.schedule_entry["id"]

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, None)
        self.assertEqual(_parent.id, self.comment["parent"]["id"])

    def test_db_get_comment_parent_with_parent_type_schedule_entry_new_schedule_entry(self):
        # change parent (schedule entry) ID to new (non-exist) ID
        self.comment["parent"]["type"] = self.schedule_entry["type"]
        self.comment["parent"]["id"] = 1

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, f'schedule entry {self.comment["parent"]["id"]} not found<br/>'
                                     f'<a href="/bc/project/{self.comment["bucket"]["id"]}/'
                                     f'schedule_entry/{self.comment["parent"]["id"]}">'
                                     f'try to open schedule entry</a> first.')
        self.assertEqual(_parent, None)

    def test_db_get_comment_parent_with_parent_type_question_answer(self):
        # change parent type to existing question_answer
        self.comment["parent"]["type"] = self.question_answer["type"]
        self.comment["parent"]["id"] = self.question_answer["id"]

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, None)
        self.assertEqual(_parent.id, self.comment["parent"]["id"])

    def test_db_get_comment_parent_with_parent_type_question_answer_new_question_answer(self):
        # change parent (question answer) ID to new (non-exist) ID
        self.comment["parent"]["type"] = self.question_answer["type"]
        self.comment["parent"]["id"] = 1

        _parent, _exception = bc.utils.db_get_comment_parent(parent=self.comment["parent"],
                                                             bucket_id=self.comment["bucket"]["id"])
        self.assertEqual(_exception, f'question answer {self.comment["parent"]["id"]} not found<br/>'
                                     f'<a href="/bc/project/{self.comment["bucket"]["id"]}/'
                                     f'question_answer/{self.comment["parent"]["id"]}">'
                                     f'try to open question answer</a> first.')
        self.assertEqual(_parent, None)

    def test_db_get_message_parent(self):
        _parent, _exception = bc.utils.db_get_message_parent(parent=self.message["parent"],
                                                             bucket_id=self.message["bucket"]["id"])

        self.assertEqual(_exception, None)
        self.assertEqual(_parent.id, self.message["parent"]["id"])

    def test_db_get_message_parent_with_parent_type_message_board_new_message_board(self):
        # change parent (message board) ID to new (non-exist) ID
        self.message["parent"]["id"] = 1

        _parent, _exception = bc.utils.db_get_message_parent(parent=self.message["parent"],
                                                             bucket_id=self.message["bucket"]["id"])
        self.assertEqual(_exception, f'message board {self.message["parent"]["id"]} not found<br/>'
                                     f'<a href="/bc/project/{self.message["bucket"]["id"]}/'
                                     f'message_board/{self.message["parent"]["id"]}">'
                                     f'try to open message board</a> first.')
        self.assertEqual(_parent, None)

    def test_db_get_message_parent_with_invalid_parent_type(self):
        # change parent type to invalid type "Cloud"
        self.message["parent"]["type"] = "Cloud"

        _parent, _exception = bc.utils.db_get_message_parent(parent=self.message["parent"],
                                                             bucket_id=self.message["bucket"]["id"])
        self.assertEqual(_exception, f'parent {self.message["parent"]["id"]} type {self.message["parent"]["type"]} not '
                                     f'in {bc.utils.static_get_message_parent_types()}.')
        self.assertEqual(_parent, None)

    def test_db_get_vault_parent(self):
        _parent, _exception = bc.utils.db_get_vault_parent(parent=self.vault["parent"],
                                                           bucket_id=self.vault["bucket"]["id"])

        self.assertEqual(_exception, None)
        self.assertEqual(_parent.id, self.vault["parent"]["id"])

    def test_db_get_vault_parent_with_parent_type_vault_new_vault(self):
        # change parent (vault) ID to new (non-exist) ID
        self.vault["parent"]["id"] = 1

        _parent, _exception = bc.utils.db_get_vault_parent(parent=self.vault["parent"],
                                                           bucket_id=self.vault["bucket"]["id"])
        self.assertEqual(_exception, f'vault {self.vault["parent"]["id"]} not found<br/>'
                                     f'<a href="/bc/project/{self.vault["bucket"]["id"]}/'
                                     f'vault/{self.vault["parent"]["id"]}">try to open vault</a> first.')
        self.assertEqual(_parent, None)

    def test_db_get_vault_parent_with_invalid_parent_type(self):
        # change parent type to invalid type "Cloud"
        self.vault["parent"]["type"] = "Cloud"

        _parent, _exception = bc.utils.db_get_vault_parent(parent=self.vault["parent"],
                                                             bucket_id=self.vault["bucket"]["id"])
        self.assertEqual(_exception, f'parent {self.vault["parent"]["id"]} type {self.vault["parent"]["type"]} not '
                                     f'in {bc.utils.static_get_vault_parent_types()}.')
        self.assertEqual(_parent, None)


class UtilsConstTest(TestCase):

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods
        pass

    def setUp(self):  # Run once for every test method to set up clean data
        pass

    def test_static_get_comment_parent_types(self):
        self.assertEqual(bc.utils.static_get_comment_parent_types(),
                         ['Document', 'Message', 'Question::Answer', 'Schedule::Entry', 'Todolist', 'Todo', 'Upload'])

    def test_static_get_message_parent_types(self):
        self.assertEqual(bc.utils.static_get_message_parent_types(), ['Message::Board'])

    def test_static_get_vault_parent_types(self):
        self.assertEqual(bc.utils.static_get_vault_parent_types(), ['Vault'])

    def test_static_get_recording_types(self):
        self.assertEqual(bc.utils.static_get_recording_types(),
                         ['Comment', 'Document', 'Message', 'Question::Answer', 'Schedule::Entry', 'Todo', 'Todolist',
                          'Upload', 'Vault'])


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
