from django.test import TestCase

from pathlib import Path
from json import loads as json_loads, dumps as json_dumps, load as json_stream_load

from bc.serializers import BcPeopleSerializer


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
