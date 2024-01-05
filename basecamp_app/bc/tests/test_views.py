from django.test import TestCase
from django.urls import reverse

from unittest.mock import patch
from pathlib import Path
from json import loads as json_loads, dumps as json_dumps, load as json_stream_load

from bc.models import BcComment


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
