from django.test import TestCase
from django.urls import reverse

from unittest.mock import patch
from pathlib import Path
from json import loads as json_loads, dumps as json_dumps, load as json_stream_load

from bc.models import BcComment


class ViewsProjectTest(TestCase):
    fixtures = ["bc_bccompany", "bc_bcpeople",
                "bc_bcproject", "bc_bcprojecttool", ]

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods

        # api_sample.json is collections of API data from bc3-api site https://github.com/basecamp/bc3-api/tree/master
        test_dir = Path(__file__).resolve().parent
        with open(test_dir / "api_sample.json") as stream:
            api_sample_json = json_stream_load(stream)

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/projects.md#get-a-project
        # the database loaded with fixture bc_bcproject.json and bc_bcprojecttool.json
        cls.project_data_2085958499 = json_dumps(api_sample_json["project"]["2085958499"])
        cls.project_data_2085958497 = json_dumps(api_sample_json["project"]["2085958497"])

    def setUp(self):  # Run once for every test method to set up clean data
        self.project = json_loads(self.project_data_2085958499)
        self.project_2085958497 = json_loads(self.project_data_2085958497)

    def test_app_project_main(self):

        with (
            patch('bc.views.project.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.project.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/projects.md
            mock_request_get.return_value.json.return_value = [
                self.project,
                self.project_2085958497,
            ]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(reverse('app-project-main'))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/">back to main</a><br/>'
                             f'<li><a href="/bc/project/{self.project["id"]}">'
                             f'{self.project["id"]}</a> {self.project["name"]}</li>'
                             f'<li><a href="/bc/project/{self.project_2085958497["id"]}">'
                             f'{self.project_2085958497["id"]}</a> {self.project_2085958497["name"]}</li>'
                             .encode(response.charset))

    def test_app_project_main_with_no_token(self):

        with (
            patch('bc.views.project.session_get_token_and_identity') as mock_get_token_and_identity
        ):
            _token = None
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(reverse('app-project-main'))

            mock_get_token_and_identity.assert_called_once()

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('bc-auth'))

    def test_app_project_main_with_response_not_ok(self):

        with (
            patch('bc.views.project.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.project.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            response_not_ok = 400
            mock_request_get.return_value.status_code = response_not_ok

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(reverse('app-project-main'))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, response_not_ok)

    def test_app_message_type_with_header_x_total_count(self):

        with (
            patch('bc.views.project.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.project.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/projects.md
            mock_request_get.return_value.json.return_value = [
                self.project,
                self.project_2085958497,
            ]
            x_total_count = 4  # dummy: 2 x 2 (paging)
            mock_request_get.return_value.headers = {
                "X-Total-Count": x_total_count,
            }

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(reverse('app-project-main'))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/">back to main</a><br/>'
                             f'total projects: {x_total_count}'
                             f'<li><a href="/bc/project/{self.project["id"]}">'
                             f'{self.project["id"]}</a> {self.project["name"]}</li>'
                             f'<li><a href="/bc/project/{self.project_2085958497["id"]}">'
                             f'{self.project_2085958497["id"]}</a> {self.project_2085958497["name"]}</li>'
                             .encode(response.charset))

    def test_app_project_detail(self):
        with (
            patch('bc.views.project.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.project.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/projects.md
            # set questionnaire enabled, to comply test
            for tool in self.project['dock']:
                if tool['id'] == 1069479343:
                    tool['enabled'] = True
            mock_request_get.return_value.json.return_value = self.project

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-project-detail',
                        kwargs={'project_id': self.project["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/project/">back</a><br/>'
                             f'project: {self.project["id"]}<br/>'
                             f'name: {self.project["name"]}<br/>'
                             f'purpose: {self.project["purpose"]}<br/>'
                             f'created_at: {self.project["created_at"]}<br/>'
                             f'enabled tools: <br/>'
                             f'<li><a href="/bc/project/{self.project["id"]}/message_board/1069479338">1069479338</a> '
                             f'Message Board (message_board)</li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/todoset/1069479339">1069479339</a> '
                             f'To-dos (todoset)</li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/vault/1069479340">1069479340</a> '
                             f'Docs &amp; Files (vault)</li>'
                             f'<li>1069479341 Campfire (chat)</li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/schedule/1069479342">1069479342</a> '
                             f'Schedule (schedule)</li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/questionnaire/1069479343">1069479343</a> '
                             f'Automatic Check-ins (questionnaire)</li><br/>'
                             f'<a href="/bc/project/{self.project["id"]}/message/type">message types</a><br/>'
                             f'recording types: <br/>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Comment">Comment</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Document">Document</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Message">Message</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Question::Answer">'
                             f'Question::Answer</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Schedule::Entry">'
                             f'Schedule::Entry</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Todo">Todo</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Todolist">Todolist</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Upload">Upload</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Vault">Vault</a></li><br/>'
                             .encode(response.charset))

    def test_app_project_detail_update_db(self):
        with (
            patch('bc.views.project.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.project.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/projects.md
            # set questionnaire enabled, to comply test
            for tool in self.project['dock']:
                if tool['id'] == 1069479343:
                    tool['enabled'] = True
            mock_request_get.return_value.json.return_value = self.project

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-project-detail-update-db',
                        kwargs={'project_id': self.project["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/project/">back</a><br/>'
                             f'project: {self.project["id"]}<br/>'
                             f'name: {self.project["name"]}<br/>'
                             f'purpose: {self.project["purpose"]}<br/>'
                             f'created_at: {self.project["created_at"]}<br/>'
                             f'enabled tools: <br/>'
                             f'<li><a href="/bc/project/{self.project["id"]}/message_board/1069479338">1069479338</a> '
                             f'Message Board (message_board)</li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/todoset/1069479339">1069479339</a> '
                             f'To-dos (todoset)</li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/vault/1069479340">1069479340</a> '
                             f'Docs &amp; Files (vault)</li>'
                             f'<li>1069479341 Campfire (chat)</li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/schedule/1069479342">1069479342</a> '
                             f'Schedule (schedule)</li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/questionnaire/1069479343">1069479343</a> '
                             f'Automatic Check-ins (questionnaire)</li><br/>'
                             f'<a href="/bc/project/{self.project["id"]}/message/type">message types</a><br/>'
                             f'recording types: <br/>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Comment">Comment</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Document">Document</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Message">Message</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Question::Answer">'
                             f'Question::Answer</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Schedule::Entry">'
                             f'Schedule::Entry</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Todo">Todo</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Todolist">Todolist</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Upload">Upload</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Vault">Vault</a></li><br/>'
                             .encode(response.charset))

    def test_app_project_detail_update_db_with_not_exist_project_and_dock(self):
        with (
            patch('bc.views.project.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.project.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/projects.md
            # set with not exist ID
            self.project['id'] = 1  # change Project ID with not exist ID
            not_exist_message_board_id = 1
            self.project['dock'][0]['id'] = not_exist_message_board_id  # change Message Board ID with not exist ID
            mock_request_get.return_value.json.return_value = self.project

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-project-detail-update-db',
                        kwargs={'project_id': self.project["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/project/">back</a><br/>'
                             f'project: {self.project["id"]}<br/>'
                             f'name: {self.project["name"]}<br/>'
                             f'purpose: {self.project["purpose"]}<br/>'
                             f'created_at: {self.project["created_at"]}<br/>'
                             f'enabled tools: <br/>'
                             f'<li><a href="/bc/project/{self.project["id"]}/message_board/'
                             f'{not_exist_message_board_id}">{not_exist_message_board_id}</a> '
                             f'Message Board (message_board)</li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/todoset/1069479339">1069479339</a> '
                             f'To-dos (todoset)</li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/vault/1069479340">1069479340</a> '
                             f'Docs &amp; Files (vault)</li>'
                             f'<li>1069479341 Campfire (chat)</li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/schedule/1069479342">1069479342</a> '
                             f'Schedule (schedule)</li><br/>'
                             f'<a href="/bc/project/{self.project["id"]}/message/type">message types</a><br/>'
                             f'recording types: <br/>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Comment">Comment</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Document">Document</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Message">Message</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Question::Answer">'
                             f'Question::Answer</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Schedule::Entry">'
                             f'Schedule::Entry</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Todo">Todo</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Todolist">Todolist</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Upload">Upload</a></li>'
                             f'<li><a href="/bc/project/{self.project["id"]}/recording/type/Vault">Vault</a></li><br/>'
                             .encode(response.charset))

    def test_app_project_detail_with_no_token(self):

        with (
            patch('bc.views.project.session_get_token_and_identity') as mock_get_token_and_identity
        ):
            _token = None
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-project-detail',
                        kwargs={'project_id': self.project["id"]}))

            mock_get_token_and_identity.assert_called_once()

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('bc-auth'))

    def test_app_project_detail_with_response_not_ok(self):

        with (
            patch('bc.views.project.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.project.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            response_not_ok = 400
            mock_request_get.return_value.status_code = response_not_ok

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-project-detail',
                        kwargs={'project_id': self.project["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, response_not_ok)


class ViewsMessageTest(TestCase):
    fixtures = ["bc_bccompany", "bc_bcpeople",
                "bc_bcproject", "bc_bcprojecttool",
                "bc_bcmessagecategory", "bc_bcmessageboard", "bc_bcmessage",]

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods

        # api_sample.json is collections of API data from bc3-api site https://github.com/basecamp/bc3-api/tree/master
        test_dir = Path(__file__).resolve().parent
        with open(test_dir / "api_sample.json") as stream:
            api_sample_json = json_stream_load(stream)

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md#get-a-message-type
        # the database loaded with fixture bc_bcmessagecategory.json
        cls.message_category_data = json_dumps(api_sample_json["message_category"]["823758531"])

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_boards.md#get-message-board
        # the database loaded with fixture bc_bcmessageboard.json
        cls.message_board_data = json_dumps(api_sample_json["message_board"]["1069479338"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md#get-a-message
        # the database loaded with fixture bc_bcmessage.json
        cls.message_data = json_dumps(api_sample_json["message"]["1069479351"])

    def setUp(self):  # Run once for every test method to set up clean data
        self.message_category = json_loads(self.message_category_data)
        self.message_board = json_loads(self.message_board_data)
        self.message = json_loads(self.message_data, strict=False)  # disable strict to process content with \n

    def test_app_message_type(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md
            mock_request_get.return_value.json.return_value = [
                {
                    "id": 823758531,
                    "name": "Announcement",
                    "icon": "📢",
                    "created_at": "2017-03-28T15:25:09.455Z",
                    "updated_at": "2017-03-28T15:25:09.455Z"
                },
                {
                    "id": 823758530,
                    "name": "Update",
                    "icon": "❤️",
                    "created_at": "2017-03-28T15:25:09.450Z",
                    "updated_at": "2017-03-28T15:25:09.450Z"
                }
            ]

            # as the message_category data did not have bucket_id, borrow from message_board data
            bucket_id = self.message_board["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(reverse('app-message-type', kwargs={'bucket_id': bucket_id}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            self.assertEqual(response.content,
                             f'<a href="/bc/project/{bucket_id}">back</a><br/>'
                             '<li>📢 Announcement</li>'
                             '<li>❤️ Update</li>'.encode(response.charset))

    def test_app_message_type_with_no_token(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity
        ):
            _token = None
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            # as the message_category data did not have bucket_id, borrow from message_board data
            bucket_id = self.message_board["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(reverse('app-message-type', kwargs={'bucket_id': bucket_id}))

            mock_get_token_and_identity.assert_called_once()

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('bc-auth'))

    def test_app_message_type_with_response_not_ok(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            response_not_ok = 400
            mock_request_get.return_value.status_code = response_not_ok

            # as the message_category data did not have bucket_id, borrow from message_board data
            bucket_id = self.message_board["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(reverse('app-message-type', kwargs={'bucket_id': bucket_id}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, response_not_ok)

    def test_app_message_type_with_header_x_total_count(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md
            mock_request_get.return_value.json.return_value = [
                {
                    "id": 823758531,
                    "name": "Announcement",
                    "icon": "📢",
                    "created_at": "2017-03-28T15:25:09.455Z",
                    "updated_at": "2017-03-28T15:25:09.455Z"
                },
                {
                    "id": 823758530,
                    "name": "Update",
                    "icon": "❤️",
                    "created_at": "2017-03-28T15:25:09.450Z",
                    "updated_at": "2017-03-28T15:25:09.450Z"
                }
            ]
            x_total_count = 4  # dummy: 2 x 2 (paging)
            mock_request_get.return_value.headers = {
                "X-Total-Count": x_total_count,
            }

            # as the message_category data did not have bucket_id, borrow from message_board data
            bucket_id = self.message_board["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(reverse('app-message-type', kwargs={'bucket_id': bucket_id}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/project/{bucket_id}">back</a><br/>total message types: {x_total_count}'
                             '<li>📢 Announcement</li>'
                             '<li>❤️ Update</li>'.encode(response.charset))

    def test_app_message_board_detail(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md
            mock_request_get.return_value.json.return_value = self.message_board

            # save bucket id before it removed (pop) on the process
            bucket_id = self.message_board["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-detail',
                        kwargs={'bucket_id': self.message_board["bucket"]["id"],
                                'message_board_id': self.message_board["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/project/{bucket_id}">back</a><br/>'
                             f'title: {self.message_board["title"]}<br/>'
                             f'type: {self.message_board["type"]}<br/>'
                             f'<a href="/bc/project/{bucket_id}/message_board/'
                             f'{self.message_board["id"]}/message">{self.message_board["messages_count"]} messages</a>'
                             f'<br/>'.encode(response.charset))

    def test_app_message_board_detail_with_no_token(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity
        ):
            _token = None
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-detail',
                        kwargs={'bucket_id': self.message_board["bucket"]["id"],
                                'message_board_id': self.message_board["id"]}))

            mock_get_token_and_identity.assert_called_once()

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('bc-auth'))

    def test_app_message_board_with_response_not_ok(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            response_not_ok = 400
            mock_request_get.return_value.status_code = response_not_ok

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-detail',
                        kwargs={'bucket_id': self.message_board["bucket"]["id"],
                                'message_board_id': self.message_board["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, response_not_ok)

    def test_app_message_board_detail_with_not_exist_bucket(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md
            mock_request_get.return_value.json.return_value = self.message_board

            # set bucket with not-exist ID
            not_exist_bucket_id = 1
            self.message_board["bucket"]["id"] = not_exist_bucket_id

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-detail',
                        kwargs={'bucket_id': self.message_board["bucket"]["id"],
                                'message_board_id': self.message_board["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'bucket {not_exist_bucket_id} not found<br/><a href="/bc/project/{not_exist_bucket_id}/'
                             f'update-db">save project to db</a> first.'.encode(response.charset))

    def test_app_message_board_detail_with_not_exist_creator(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md
            mock_request_get.return_value.json.return_value = self.message_board

            # set bucket with not-exist ID, remove the creator company as it will trigger error
            not_exist_creator_id = 1
            self.message_board["creator"]["id"] = not_exist_creator_id
            self.message_board["creator"].pop("company")

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-detail',
                        kwargs={'bucket_id': self.message_board["bucket"]["id"],
                                'message_board_id': self.message_board["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             "creator serializer error: {'people company error': "
                             "ErrorDetail(string='people no company field', code='invalid')}".encode(response.charset))

    def test_app_message_board_detail_with_new_message_board(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md
            mock_request_get.return_value.json.return_value = self.message_board

            # set message board with not-exist ID, message board will be created inside the process
            not_exist_message_board_id = 1
            self.message_board["id"] = not_exist_message_board_id

            # save bucket id before it removed (pop) on the process
            bucket_id = self.message_board["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-detail',
                        kwargs={'bucket_id': self.message_board["bucket"]["id"],
                                'message_board_id': self.message_board["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/project/{bucket_id}">back</a><br/>'
                             f'title: {self.message_board["title"]}<br/>'
                             f'type: {self.message_board["type"]}<br/>'
                             f'<a href="/bc/project/{bucket_id}/message_board/'
                             f'{self.message_board["id"]}/message">{self.message_board["messages_count"]} messages</a>'
                             f'<br/>'.encode(response.charset))

    def test_app_message_board_message(self):
        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md
            mock_request_get.return_value.json.return_value = [
                self.message,
            ]

            # save bucket id before it removed (pop) on the process
            bucket_id = self.message["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-message',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_board_id': self.message["parent"]["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/project/{bucket_id}/message_board/{self.message["parent"]["id"]}">back</a>'
                             f'<br/><li><a href="/bc/project/{bucket_id}/message/{self.message["id"]}">'
                             f'{self.message["id"]}</a> We won Leto! (db)</li>'.encode(response.charset))

    def test_app_message_board_message_with_no_token(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity
        ):
            _token = None
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-message',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_board_id': self.message["parent"]["id"]}))

            mock_get_token_and_identity.assert_called_once()

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('bc-auth'))

    def test_app_message_board_message_with_response_not_ok(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            response_not_ok = 400
            mock_request_get.return_value.status_code = response_not_ok

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-message',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_board_id': self.message["parent"]["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, response_not_ok)

    def test_app_message_board_message_with_not_exist_bucket(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md
            # set bucket with not-exist ID
            not_exist_bucket_id = 1
            self.message["bucket"]["id"] = not_exist_bucket_id
            mock_request_get.return_value.json.return_value = [
                self.message,
            ]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-message',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_board_id': self.message["parent"]["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'bucket {not_exist_bucket_id} not found<br/><a href="/bc/project/{not_exist_bucket_id}/'
                             f'update-db">save project to db</a> first.'.encode(response.charset))

    def test_app_message_board_message_with_not_exist_message_board(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md
            # set bucket with not-exist ID
            not_exist_message_board_id = 1
            self.message["parent"]["id"] = not_exist_message_board_id
            mock_request_get.return_value.json.return_value = [
                self.message,
            ]

            # save bucket id before it removed (pop) on the process
            bucket_id = self.message["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-message',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_board_id': self.message["parent"]["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'message board not found, id: {not_exist_message_board_id}<br/>'
                             f'<a href="/bc/project/{bucket_id}/message_board/{not_exist_message_board_id}">'
                             f'try to open message board</a> first.'.encode(response.charset))

    def test_app_message_board_message_with_header_x_total_count(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md
            mock_request_get.return_value.json.return_value = [
                self.message,
            ]
            x_total_count = 2  # dummy: 1 x 2 (paging)
            mock_request_get.return_value.headers = {
                "X-Total-Count": x_total_count,
            }

            # save bucket id before it removed (pop) on the process
            bucket_id = self.message["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-board-message',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_board_id': self.message["parent"]["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/project/{bucket_id}/message_board/{self.message["parent"]["id"]}">back</a>'
                             f'<br/>total messages: {x_total_count}'
                             f'<li><a href="/bc/project/{bucket_id}/message/{self.message["id"]}">{self.message["id"]}'
                             f'</a> We won Leto! (db)</li>'.encode(response.charset))

    def test_app_message_detail(self):
        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md
            mock_request_get.return_value.json.return_value = self.message

            # save bucket id before it removed (pop) on the process
            bucket_id = self.message["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-detail',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_id': self.message["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/project/{bucket_id}">back</a><br/>'
                             f'title: {self.message["title"]}<br/>type: {self.message["type"]}<br/>'
                             f'comments_count: {self.message["comments_count"]}<br/>'.encode(response.charset))

    def test_app_message_detail_with_no_token(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity
        ):
            _token = None
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-detail',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_id': self.message["id"]}))

            mock_get_token_and_identity.assert_called_once()

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('bc-auth'))

    def test_app_message_detail_with_response_not_ok(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            response_not_ok = 400
            mock_request_get.return_value.status_code = response_not_ok

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-detail',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_id': self.message["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, response_not_ok)

    def test_app_message_detail_with_not_exist_bucket(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md
            # set bucket with not-exist ID
            not_exist_bucket_id = 1
            self.message["bucket"]["id"] = not_exist_bucket_id
            mock_request_get.return_value.json.return_value = self.message

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-detail',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_id': self.message["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'bucket {not_exist_bucket_id} not found<br/><a href="/bc/project/{not_exist_bucket_id}/'
                             f'update-db">save project to db</a> first.'.encode(response.charset))

    def test_app_message_detail_with_invalid_parent_type(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md
            # set parent type with invalid type "Cloud"
            self.message["parent"]["type"] = "Cloud"
            mock_request_get.return_value.json.return_value = self.message

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-detail',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_id': self.message["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'message {self.message["title"]} has no creator or bucket type Project or '
                             f'parent type Message::Board'.encode(response.charset))

    def test_app_message_detail_with_not_exist_message_board(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md
            # set bucket with not-exist ID
            not_exist_message_board_id = 1
            self.message["parent"]["id"] = not_exist_message_board_id
            mock_request_get.return_value.json.return_value = self.message

            # save bucket id before it removed (pop) on the process
            bucket_id = self.message["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-detail',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_id': self.message["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'message board not found: {self.message["parent"]}<br/>'
                             f'<a href="/bc/project/{bucket_id}/message_board/{not_exist_message_board_id}">'
                             f'try to open message board</a> first.'.encode(response.charset))

    def test_app_message_detail_with_not_exist_creator(self):

        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md
            mock_request_get.return_value.json.return_value = self.message

            # set bucket with not-exist ID, remove the creator company as it will trigger error
            not_exist_creator_id = 1
            self.message["creator"]["id"] = not_exist_creator_id
            self.message["creator"].pop("company")

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-detail',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_id': self.message["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             "creator serializer error: {'people company error': "
                             "ErrorDetail(string='people no company field', code='invalid')}".encode(response.charset))

    def test_app_message_detail_with_category(self):
        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md
            self.message['category'] = self.message_category
            mock_request_get.return_value.json.return_value = self.message

            # save bucket id before it removed (pop) on the process
            bucket_id = self.message["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-detail',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_id': self.message["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/project/{bucket_id}">back</a><br/>'
                             f'title: {self.message["title"]}<br/>type: {self.message["type"]}<br/>'
                             f'comments_count: {self.message["comments_count"]}<br/>'.encode(response.charset))

    def test_app_message_detail_with_not_exist_category(self):
        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md
            # set with not-exist ID
            self.message_category['id'] = 1
            self.message['category'] = self.message_category
            mock_request_get.return_value.json.return_value = self.message

            # save bucket id before it removed (pop) on the process
            bucket_id = self.message["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-detail',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_id': self.message["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'message category not found: {self.message_category}<br/>'
                             f'<a href="/bc/project/{bucket_id}/message/type">save message types to db</a>'
                             f' first.'.encode(response.charset))

    def test_app_message_detail_with_not_exist_message(self):
        with (
            patch('bc.views.message.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.message.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md
            # set with not-exist ID, will be created in the process
            self.message['id'] = 1
            mock_request_get.return_value.json.return_value = self.message

            # save bucket id before it removed (pop) on the process
            bucket_id = self.message["bucket"]["id"]

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-message-detail',
                        kwargs={'bucket_id': self.message["bucket"]["id"],
                                'message_id': self.message["id"]}))

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            # print(response.content.decode(response.charset))
            self.assertEqual(response.content,
                             f'<a href="/bc/project/{bucket_id}">back</a><br/>'
                             f'title: {self.message["title"]}<br/>type: {self.message["type"]}<br/>'
                             f'comments_count: {self.message["comments_count"]}<br/>'.encode(response.charset))


class ViewsCommentTest(TestCase):
    fixtures = ["bc_bccompany", "bc_bcpeople",
                "bc_bcproject", "bc_bcprojecttool",
                "bc_bcmessagecategory", "bc_bcmessageboard", "bc_bcmessage",
                "bc_bccomment",]

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods

        # api_sample.json is collections of API data from bc3-api site https://github.com/basecamp/bc3-api/tree/master
        test_dir = Path(__file__).resolve().parent
        with open(test_dir / "api_sample.json") as stream:
            api_sample_json = json_stream_load(stream)

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/comments.md#get-a-comment
        # the database loaded with fixture bc_bccomment.json
        cls.comment_data = json_dumps(api_sample_json["comment"]["1069479361"])

    def setUp(self):  # Run once for every test method to set up clean data
        self.comment = json_loads(self.comment_data)

    def test_app_comment_detail(self):

        with (
            patch('bc.views.comment.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.comment.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            mock_request_get.return_value.json.return_value = self.comment

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-comment-detail',
                        kwargs={'bucket_id': self.comment["bucket"]["id"], 'comment_id': self.comment["id"]})
            )

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            self.assertEqual(response.content,
                             '<a href="/bc/project/2085958499">back</a><br/>title: Re: We won Leto!<br/>parent: '
                             '<a href="#" target="_black">Message 1069479351</a><br/>'.encode(response.charset))

    def test_app_comment_detail_with_no_token(self):

        with (
            patch('bc.views.comment.session_get_token_and_identity') as mock_get_token_and_identity
        ):
            _token = None
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-comment-detail',
                        kwargs={'bucket_id': self.comment["bucket"]["id"], 'comment_id': self.comment["id"]})
            )

            mock_get_token_and_identity.assert_called_once()

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('bc-auth'))

    def test_app_comment_detail_with_response_not_ok(self):

        with (
            patch('bc.views.comment.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.comment.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 400

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-comment-detail',
                        kwargs={'bucket_id': self.comment["bucket"]["id"], 'comment_id': self.comment["id"]})
            )

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)

    def test_app_comment_detail_with_not_exist_bucket(self):

        with (
            patch('bc.views.comment.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.comment.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # change the bucket ID to new (non-exist) ID
            self.comment["bucket"]["id"] = 1
            mock_request_get.return_value.json.return_value = self.comment

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-comment-detail',
                        kwargs={'bucket_id': self.comment["bucket"]["id"], 'comment_id': self.comment["id"]})
            )

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            self.assertEqual(response.content,
                             'bucket 1 not found<br/><a href="/bc/project/1/update-db">save project to db</a>'
                             ' first.'.encode(response.charset))

    def test_app_comment_detail_with_not_exist_parent(self):

        with (
            patch('bc.views.comment.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.comment.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # change the parent ID to new (non-exist) ID
            self.comment["parent"]["id"] = 1
            mock_request_get.return_value.json.return_value = self.comment

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-comment-detail',
                        kwargs={'bucket_id': self.comment["bucket"]["id"], 'comment_id': self.comment["id"]})
            )

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            self.assertEqual(response.content,
                             'Message 1 not found<br/><a href="/bc/project/2085958499/message/1">try to open '
                             'Message</a> first.'.encode(response.charset))

    def test_app_comment_detail_with_new_creator_no_company(self):

        with (
            patch('bc.views.comment.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.comment.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # change the parent ID to new (non-exist) ID and remove the company to make serializer error
            self.comment["creator"]["id"] = 1
            self.comment["creator"].pop('company')
            mock_request_get.return_value.json.return_value = self.comment

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-comment-detail',
                        kwargs={'bucket_id': self.comment["bucket"]["id"], 'comment_id': self.comment["id"]})
            )

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            self.assertEqual(response.content,
                             "creator serializer error: {'people company error': "
                             "ErrorDetail(string='people no company field', code='invalid')}".encode(response.charset))

    def test_app_comment_detail_with_no_creator(self):

        with (
            patch('bc.views.comment.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.comment.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # remove the creator to trigger "else" because of no creator
            self.comment.pop('creator')
            mock_request_get.return_value.json.return_value = self.comment

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-comment-detail',
                        kwargs={'bucket_id': self.comment["bucket"]["id"], 'comment_id': self.comment["id"]})
            )

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 400)
            # response.charset = utf-8
            self.assertEqual(response.content,
                             "comment Re: We won Leto! has no creator or bucket type Project or parent type in "
                             "['Document', 'Message', 'Question::Answer', 'Schedule::Entry', 'Todolist', 'Todo', "
                             "'Upload']".encode(response.charset))

    def test_app_comment_detail_with_not_exist_comment(self):

        with (
            patch('bc.views.comment.session_get_token_and_identity') as mock_get_token_and_identity,
            patch('bc.views.comment.bc_api_get') as mock_request_get
        ):
            _token = {'access_token': 'access token', }
            _identity = {'id': 1, }
            mock_get_token_and_identity.return_value = _token, _identity

            mock_request_get.return_value.status_code = 200
            # change the comment ID to new (non-exist) ID, comment will be created
            self.comment["id"] = 1
            mock_request_get.return_value.json.return_value = self.comment

            # response: https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse
            response = self.client.get(
                reverse('app-comment-detail',
                        kwargs={'bucket_id': self.comment["bucket"]["id"], 'comment_id': self.comment["id"]})
            )

            mock_get_token_and_identity.assert_called_once()
            mock_request_get.assert_called_once()

            self.assertEqual(response.status_code, 200)
            # response.charset = utf-8
            self.assertEqual(response.content,
                             '<a href="/bc/project/2085958499">back</a><br/>title: Re: We won Leto!<br/>parent: '
                             '<a href="#" target="_black">Message 1069479351</a><br/>'.encode(response.charset))

            # make sure the new comment created
            _comment = BcComment.objects.get(pk=self.comment["id"])
            self.assertEqual(_comment.title, self.comment["title"])
