from django.test import TestCase, override_settings

from rest_framework.exceptions import ValidationError

from pathlib import Path
from json import loads as json_loads, dumps as json_dumps, load as json_stream_load

from bc.serializers import BcPeopleSerializer, BcWebhookSerializer


class WebhookSerializerTest(TestCase):
    fixtures = ["bc_bccompany", "bc_bcpeople", "bc_bcproject", "bc_bcprojecttool",
                "bc_bcvault", "bc_bctodolist"]

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods

        # api_sample.json is collections of API data from bc3-api site https://github.com/basecamp/bc3-api/tree/master
        test_dir = Path(__file__).resolve().parent
        with open(test_dir / "api_sample.json") as stream:
            api_sample_json = json_stream_load(stream)

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/webhooks.md
        cls.webhook_data_1479523571 = json_dumps(api_sample_json["webhook"]["1479523571"])  # "kind": "todo_copied"
        # dummy API data with "kind": "cloud_file_created"
        cls.webhook_data_1479523572 = json_dumps(api_sample_json["webhook"]["1479523572"])

    def setUp(self):  # Run once for every test method to set up clean data
        self.webhook_1479523571 = json_loads(self.webhook_data_1479523571)
        self.webhook_1479523572 = json_loads(self.webhook_data_1479523572)

    def test_deserialize_to_internal_value(self):

        serializer = BcWebhookSerializer(data=self.webhook_1479523571)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_without_recording_bucket(self):
        """
        without recording bucket should be invalid serializer
        :return:
        """

        self.webhook_1479523571["recording"].pop('bucket')  # remove bucket from webhook recording

        serializer = BcWebhookSerializer(data=self.webhook_1479523571)
        self.assertFalse(serializer.is_valid())

    def test_deserialize_to_internal_value_get_recording_base_child_with_invalid_recording_type(self):
        serializer = BcWebhookSerializer(data=self.webhook_1479523571)
        # manually call get webhook recording base child, with incorrect type of recording (not child of base)
        serializer.get_webhook_recording_base_child(recording=self.webhook_1479523571["recording"])
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_create_recording_base_child_with_invalid_recording_type(self):
        """
        with invalid recording type should be invalid serializer
        :return:
        """
        serializer = BcWebhookSerializer(data=self.webhook_1479523571)
        # manually call create webhook recording base child, with incorrect type of recording (not child of base)
        serializer.create_webhook_recording_base_child(recording=self.webhook_1479523571["recording"])
        self.assertFalse(serializer.is_valid())

    @override_settings(INSTALLED_APPS=[])
    def test_deserialize_to_internal_value_with_app_not_installed(self):

        serializer = BcWebhookSerializer(data=self.webhook_1479523571)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_recording_base_children(self):
        serializer = BcWebhookSerializer(data=self.webhook_1479523572)
        self.assertTrue(serializer.is_valid())

    @override_settings(INSTALLED_APPS=[])
    def test_deserialize_to_internal_value_recording_base_children_with_app_not_installed(self):

        serializer = BcWebhookSerializer(data=self.webhook_1479523572)
        self.assertTrue(serializer.is_valid())

    @override_settings(INSTALLED_APPS=[])
    def test_deserialize_to_internal_value_recording_base_children_create_model_with_app_not_installed(self):
        """
        construct BcWebhookSerializer with recording base child include call of create_webhook_recording_base_child().
        with django app bc not installed, not include call of _create_webhook_recording_base_child_model().
        test with call _create_webhook_recording_base_child_model() manually, without _bucket, _creator, _parent.
        :return:
        """
        serializer = BcWebhookSerializer(data=self.webhook_1479523572)
        serializer._create_webhook_recording_base_child_model(
            recording=self.webhook_1479523572["recording"], _bucket=None, _creator=None, _parent=None)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_recording_base_children_with_invalid_bucket(self):
        """
        without recording bucket should be invalid serializer
        test the ability of method db_get_recording_bucket handle non-existence or invalid type,
        by manually call method create_webhook_recording_base_child as the parent of db_get_recording_bucket
        :return:
        """
        # remove the recording bucket
        bucket_data = self.webhook_1479523572["recording"].pop('bucket')
        serializer = BcWebhookSerializer(data=self.webhook_1479523572)
        # to_internal_value() already check the bucket existence and the bucket type, test with manually call the method
        serializer.create_webhook_recording_base_child(recording=self.webhook_1479523572["recording"])
        self.assertFalse(serializer.is_valid())

        self.webhook_1479523572 = json_loads(self.webhook_data_1479523572)  # reload the data
        # re-entry the recording bucket with invalid bucket type (!= Project)
        self.webhook_1479523572["recording"]["bucket"]["type"] = '!Project'
        serializer = BcWebhookSerializer(data=self.webhook_1479523572)
        # to_internal_value() already check the bucket existence and the bucket type, test with manually call the method
        serializer.create_webhook_recording_base_child(recording=self.webhook_1479523572["recording"])
        self.assertFalse(serializer.is_valid())

    def test_deserialize_to_internal_value_with_invalid_recording_type(self):
        # change recording type from CloudFile to invalid type (Cloud)
        self.webhook_1479523572["recording"]["type"] = "Cloud"

        serializer = BcWebhookSerializer(data=self.webhook_1479523572)

        # even though the recording type invalid, the serializer still, it will only save the raw data, but no recording
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.recording, None)

    def test_deserialize_to_internal_value_with_not_exist_recording_bucket(self):
        # change recording bucket id with id that is not exist on db
        self.webhook_1479523572["recording"]["bucket"]["id"] = 1

        serializer = BcWebhookSerializer(data=self.webhook_1479523572)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_with_not_exist_recording_parent(self):
        # change recording parent id with id that is not exist on db
        self.webhook_1479523572["recording"]["parent"]["id"] = 1

        serializer = BcWebhookSerializer(data=self.webhook_1479523572)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_without_recording_creator(self):
        # change recording creator by remove the creator field
        self.webhook_1479523572["recording"].pop("creator")

        serializer = BcWebhookSerializer(data=self.webhook_1479523572)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_with_not_exist_recording_creator(self):
        # change recording creator id with id that is not exist on db
        self.webhook_1479523572["recording"]["creator"]["id"] = 1

        serializer = BcWebhookSerializer(data=self.webhook_1479523572)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_with_not_exist_recording_creator_no_company(self):
        # change recording creator id with id that is not exist on db and remove company from creator
        self.webhook_1479523572["recording"]["creator"]["id"] = 1
        self.webhook_1479523572["recording"]["creator"].pop('company')

        serializer = BcWebhookSerializer(data=self.webhook_1479523572)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_with_no_parent(self):
        # change recording parent by removing parent field
        self.webhook_1479523572["recording"].pop('parent')

        serializer = BcWebhookSerializer(data=self.webhook_1479523572)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_with_invalid_recording_parent_type(self):
        # change recording parent type from Vault to invalid type (Cloud)
        self.webhook_1479523572["recording"]["parent"]["type"] = "Cloud"

        serializer = BcWebhookSerializer(data=self.webhook_1479523572)

        # even though the recording parent type invalid, the serializer still valid,
        # it will only save the raw data, but no recording
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.recording, None)

    def test_deserialize_to_create_with_exist_person(self):
        serializer = BcWebhookSerializer(data=self.webhook_1479523571)
        if serializer.is_valid():
            webhook = serializer.save()  # save will call create
            self.assertEqual(webhook.id, self.webhook_1479523571["id"])
        else:
            self.fail(f'serializer error: {serializer.errors}')

    def test_deserialize_to_create_with_new_person_exist_company(self):
        """
        deserialize with new person (new people id) that does not exist in fixture, with existing company
        :return:
        """

        new_person_data = """{
            "id": 1049715969,
            "attachable_sgid": "BAh7CEkiCGdpZAY6BkVUSSIrZ2lkOi8vYmMzL1BlcnNvbi8xMDQ5NzE1OTY5P2V4cGlyZXNfaW4GOwBUSSIMcHVycG9zZQY7AFRJIg9hdHRhY2hhYmxlBjsAVEkiD2V4cGlyZXNfYXQGOwBUMA==--f94940da9b0adc1ec997382934419905904c8692",
            "name": "Victor Copper",
            "email_address": "victor@hanchodesign.com",
            "personable_type": "User",
            "title": "Prankster",
            "bio": null,
            "location": null,
            "created_at": "2022-11-22T17:56:23.633Z",
            "updated_at": "2022-11-22T17:56:23.633Z",
            "admin": false,
            "owner": false,
            "client": false,
            "employee": false,
            "time_zone": "America/Chicago",
            "avatar_url": "https://3.basecamp-static.com/195539477/people/BAhpBAFlkT4=--b48efd42c6425ae51e7205e157d902971934e5b8/avatar?v=1",
            "company": {
                "id": 1033447817,
                "name": "Honcho Design"
            },
            "can_manage_projects": true,
            "can_manage_people": true
        }"""
        new_person = json_loads(new_person_data)

        # change webhook creator with new_person data
        self.webhook_1479523571['creator'] = new_person

        serializer = BcWebhookSerializer(data=self.webhook_1479523571)
        if serializer.is_valid():
            webhook = serializer.save()  # save will call create
            self.assertEqual(webhook.creator.id, new_person['id'])
        else:
            self.fail(f'serializer error: {serializer.errors}')

    def test_deserialize_to_create_with_new_person_no_company(self):
        """
        deserialize with new person (new people id) that does not exist in fixture, with no company to trigger error
        :return:
        """

        new_person_data = """{
            "id": 1049715969,
            "attachable_sgid": "BAh7CEkiCGdpZAY6BkVUSSIrZ2lkOi8vYmMzL1BlcnNvbi8xMDQ5NzE1OTY5P2V4cGlyZXNfaW4GOwBUSSIMcHVycG9zZQY7AFRJIg9hdHRhY2hhYmxlBjsAVEkiD2V4cGlyZXNfYXQGOwBUMA==--f94940da9b0adc1ec997382934419905904c8692",
            "name": "Victor Copper",
            "email_address": "victor@hanchodesign.com",
            "personable_type": "User",
            "title": "Prankster",
            "bio": null,
            "location": null,
            "created_at": "2022-11-22T17:56:23.633Z",
            "updated_at": "2022-11-22T17:56:23.633Z",
            "admin": false,
            "owner": false,
            "client": false,
            "employee": false,
            "time_zone": "America/Chicago",
            "avatar_url": "https://3.basecamp-static.com/195539477/people/BAhpBAFlkT4=--b48efd42c6425ae51e7205e157d902971934e5b8/avatar?v=1",
            "can_manage_projects": true,
            "can_manage_people": true
        }"""
        new_person = json_loads(new_person_data)

        # change webhook creator with new_person data
        self.webhook_1479523571['creator'] = new_person

        serializer = BcWebhookSerializer(data=self.webhook_1479523571)
        if serializer.is_valid():
            try:
                serializer.save()  # save will call create, but ValidationError
            except ValidationError as e:
                self.assertEqual(str(e), "{'People Serializer error': {'people company error': "
                                         "ErrorDetail(string='people no company field', code='invalid')}}")
        else:
            self.fail(f'serializer error: {serializer.errors}')


class PeopleSerializerTest(TestCase):
    fixtures = ["bc_bccompany", "bc_bcpeople"]

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods

        # api_sample.json is collections of API data from bc3-api site https://github.com/basecamp/bc3-api/tree/master
        test_dir = Path(__file__).resolve().parent
        with open(test_dir / "api_sample.json") as stream:
            api_sample_json = json_stream_load(stream)

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/people.md
        cls.person_data = json_dumps(api_sample_json["person"]["1049715914"])  # "name": "Victor Cooper"

    def setUp(self):  # Run once for every test method to set up clean data
        self.person = json_loads(self.person_data)

    def test_deserialize_to_internal_value(self):

        serializer = BcPeopleSerializer(data=self.person)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_with_new_company(self):
        """
        change company with data that does not exist in fixture
        :return:
        """

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/people.md
        new_company_data = {"id": 1033447819, "name": "Hancho Design"}
        self.person['company'] = new_company_data

        serializer = BcPeopleSerializer(data=self.person)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_with_key_can_ping(self):
        if 'can_ping' not in self.person:
            self.person['can_ping'] = True

        serializer = BcPeopleSerializer(data=self.person)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_internal_value_with_key_out_of_office(self):
        if 'out_of_office' not in self.person:
            self.person['out_of_office'] = {}

        serializer = BcPeopleSerializer(data=self.person)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_to_create_with_exist_person(self):
        serializer = BcPeopleSerializer(data=self.person)
        if serializer.is_valid():
            person = serializer.save()
            self.assertEqual(person.id, self.person["id"])
        else:
            self.fail(f'serializer error: {serializer.errors}')

    def test_deserialize_to_create_with_new_person_new_company(self):
        """
        deserialize with new person (new people id, new company) that does not exist in fixture
        :return:
        """

        new_person_data = """{
            "id": 1049715969,
            "attachable_sgid": "BAh7CEkiCGdpZAY6BkVUSSIrZ2lkOi8vYmMzL1BlcnNvbi8xMDQ5NzE1OTY5P2V4cGlyZXNfaW4GOwBUSSIMcHVycG9zZQY7AFRJIg9hdHRhY2hhYmxlBjsAVEkiD2V4cGlyZXNfYXQGOwBUMA==--f94940da9b0adc1ec997382934419905904c8692",
            "name": "Victor Copper",
            "email_address": "victor@hanchodesign.com",
            "personable_type": "User",
            "title": "Prankster",
            "bio": null,
            "location": null,
            "created_at": "2022-11-22T17:56:23.633Z",
            "updated_at": "2022-11-22T17:56:23.633Z",
            "admin": false,
            "owner": false,
            "client": false,
            "employee": false,
            "time_zone": "America/Chicago",
            "avatar_url": "https://3.basecamp-static.com/195539477/people/BAhpBAFlkT4=--b48efd42c6425ae51e7205e157d902971934e5b8/avatar?v=1",
            "company": {
                "id": 1033447819,
                "name": "Hancho Design"
            },
            "can_manage_projects": true,
            "can_manage_people": true
        }"""
        new_person = json_loads(new_person_data)

        serializer = BcPeopleSerializer(data=new_person)
        if serializer.is_valid():
            person = serializer.save()
            self.assertEqual(person.id, new_person["id"])
        else:
            self.fail(f'serializer error: {serializer.errors}')

    def test_deserialize_to_create_with_new_person_exist_company(self):
        """
        deserialize with new person (new people id) that does not exist in fixture, with existing company
        :return:
        """

        new_person_data = """{
            "id": 1049715969,
            "attachable_sgid": "BAh7CEkiCGdpZAY6BkVUSSIrZ2lkOi8vYmMzL1BlcnNvbi8xMDQ5NzE1OTY5P2V4cGlyZXNfaW4GOwBUSSIMcHVycG9zZQY7AFRJIg9hdHRhY2hhYmxlBjsAVEkiD2V4cGlyZXNfYXQGOwBUMA==--f94940da9b0adc1ec997382934419905904c8692",
            "name": "Victor Copper",
            "email_address": "victor@hanchodesign.com",
            "personable_type": "User",
            "title": "Prankster",
            "bio": null,
            "location": null,
            "created_at": "2022-11-22T17:56:23.633Z",
            "updated_at": "2022-11-22T17:56:23.633Z",
            "admin": false,
            "owner": false,
            "client": false,
            "employee": false,
            "time_zone": "America/Chicago",
            "avatar_url": "https://3.basecamp-static.com/195539477/people/BAhpBAFlkT4=--b48efd42c6425ae51e7205e157d902971934e5b8/avatar?v=1",
            "company": {
                "id": 1033447817,
                "name": "Honcho Design"
            },
            "can_manage_projects": true,
            "can_manage_people": true
        }"""
        new_person = json_loads(new_person_data)

        serializer = BcPeopleSerializer(data=new_person)
        if serializer.is_valid():
            person = serializer.save()
            self.assertEqual(person.id, new_person["id"])
        else:
            self.fail(f'serializer error: {serializer.errors}')

    def test_deserialize_to_create_with_exist_email_address(self):
        """
        deserialize with new person (new people id) that the email address already exist at fixture
        :return:
        """

        new_person_data = """{
            "id": 1,
            "attachable_sgid": "BAh7CEkiCGdpZAY6BkVUSSIrZ2lkOi8vYmMzL1BlcnNvbi8xMDQ5NzE1OTE0P2V4cGlyZXNfaW4GOwBUSSIMcHVycG9zZQY7AFRJIg9hdHRhY2hhYmxlBjsAVEkiD2V4cGlyZXNfYXQGOwBUMA==--ff006accb6e013cca785190fa38f42c091d24f1e",
            "name": "Victor Cooper",
            "email_address": "victor@honchodesign.com",
            "personable_type": "User",
            "title": "Chief Strategist",
            "bio": "Don’t let your dreams be dreams",
            "location": "Chicago, IL",
            "created_at": "2022-11-22T08:23:21.732Z",
            "updated_at": "2022-11-22T08:23:21.904Z",
            "admin": true,
            "owner": true,
            "client": false,
            "employee": true,
            "time_zone": "America/Chicago",
            "avatar_url": "https://3.basecamp-static.com/195539477/people/BAhpBMpkkT4=--5520caeec1845b5090bbfc993ffe8eca8d138e14/avatar?v=1",
            "company": {
                "id": 1033447817,
                "name": "Honcho Design"
            },
            "can_manage_projects": true,
            "can_manage_people": true
        }"""
        new_person = json_loads(new_person_data)

        serializer = BcPeopleSerializer(data=new_person)
        if serializer.is_valid():
            person = serializer.save()
            self.assertEqual(person.email_address, new_person["email_address"])
        else:
            self.fail(f'serializer error: {serializer.errors}')
