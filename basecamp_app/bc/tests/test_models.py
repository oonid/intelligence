from django.test import TestCase

from json import loads as json_loads

from bc.models import BcCompany, BcPeople


class CompanyTest(TestCase):
    # sample from https://github.com/basecamp/bc3-api/blob/master/sections/people.md
    company_id = 1033447817
    company_name = 'Honcho Design'

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods
        _ = BcCompany.objects.create(id=cls.company_id, name=cls.company_name)

    def setUp(self):  # Run once for every test method to set up clean data
        pass

    def test_company_id_and_name(self):
        try:
            _company = BcCompany.objects.get(id=self.company_id)
            self.assertEqual(_company.id, self.company_id)
            self.assertEqual(_company.name, self.company_name)
        except BcCompany.DoesNotExist:
            self.fail(msg=f'company with id {self.company_id} not found.')

    def test_company_str(self):
        try:
            _company = BcCompany.objects.get(id=self.company_id)
            self.assertEqual(str(_company), f'{self.company_id} {self.company_name}')
        except BcCompany.DoesNotExist:
            self.fail(msg=f'company with id {self.company_id} not found.')


class PeopleTest(TestCase):
    # sample from https://github.com/basecamp/bc3-api/blob/master/sections/people.md
    person_data = """{
        "id": 1049715914,
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
    person = None

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods
        _person = json_loads(cls.person_data)
        _company = BcCompany.objects.create(**_person["company"])
        _person.pop("company")  # remove key "company" from person, use _company object
        _ = BcPeople.objects.create(company=_company, **_person)

    def setUp(self):  # Run once for every test method to set up clean data
        self.person = json_loads(self.person_data)

    def test_people_id_and_name(self):
        try:
            _person = BcPeople.objects.get(id=self.person["id"])
            self.assertEqual(_person.id, self.person["id"])
            self.assertEqual(_person.name, self.person["name"])
        except BcCompany.DoesNotExist:
            self.fail(msg=f'person with id {self.person["id"]} not found.')

    def test_people_str(self):
        try:
            _person = BcPeople.objects.get(id=self.person["id"])
            self.assertEqual(str(_person),
                             f'{self.person["id"]} {self.person["name"]} {self.person["email_address"]}')
        except BcCompany.DoesNotExist:
            self.fail(msg=f'person with id {self.person["id"]} not found.')
