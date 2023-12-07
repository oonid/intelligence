from django.test import TestCase

from json import loads as json_loads

from bc.models import BcCompany, BcPeople, BcProjectTool, BcProject


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
        except BcPeople.DoesNotExist:
            self.fail(msg=f'person with id {self.person["id"]} not found.')

    def test_people_str(self):
        try:
            _person = BcPeople.objects.get(id=self.person["id"])
            self.assertEqual(str(_person),
                             f'{self.person["id"]} {self.person["name"]} {self.person["email_address"]}')
        except BcPeople.DoesNotExist:
            self.fail(msg=f'person with id {self.person["id"]} not found.')


class ProjectToolTest(TestCase):
    # sample from https://github.com/basecamp/bc3-api/blob/master/sections/projects.md#get-a-project
    tool_data = """{
        "id": 1069479338,
        "title": "Message Board",
        "name": "message_board",
        "enabled": true,
        "position": 1,
        "url": "https://3.basecampapi.com/195539477/buckets/2085958499/message_boards/1069479338.json",
        "app_url": "https://3.basecamp.com/195539477/buckets/2085958499/message_boards/1069479338"
    }"""
    tool = None

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods
        _tool = json_loads(cls.tool_data)
        _ = BcProjectTool.objects.create(**_tool)

    def setUp(self):  # Run once for every test method to set up clean data
        self.tool = json_loads(self.tool_data)

    def test_project_tool_id_and_name(self):
        try:
            _tool = BcProjectTool.objects.get(id=self.tool["id"])
            self.assertEqual(_tool.id, self.tool["id"])
            self.assertEqual(_tool.name, self.tool["name"])
            self.assertEqual(_tool.title, self.tool["title"])
            self.assertEqual(_tool.enabled, self.tool["enabled"])
        except BcProjectTool.DoesNotExist:
            self.fail(msg=f'tool with id {self.tool["id"]} not found.')

    def test_project_tool_str(self):
        try:
            _tool = BcProjectTool.objects.get(id=self.tool["id"])
            self.assertEqual(str(_tool),
                             f'{self.tool["id"]} {self.tool["name"]} {self.tool["title"]} ({self.tool["enabled"]})')
        except BcProjectTool.DoesNotExist:
            self.fail(msg=f'tool with id {self.tool["id"]} not found.')


class ProjectTest(TestCase):
    # sample from https://github.com/basecamp/bc3-api/blob/master/sections/projects.md#get-a-project
    project_data = """{
        "id": 2085958499,
        "status": "active",
        "created_at": "2022-10-28T08:23:58.169Z",
        "updated_at": "2022-11-22T17:56:27.363Z",
        "name": "The Leto Laptop",
        "description": "Laptop product launch.",
        "purpose": "topic",
        "clients_enabled": false,
        "bookmark_url": "https://3.basecampapi.com/195539477/my/bookmarks/BAh7CEkiCGdpZAY6BkVUSSIrZ2lkOi8vYmMzL0J1Y2tldC8yMDg1OTU4NDk5P2V4cGlyZXNfaW4GOwBUSSIMcHVycG9zZQY7AFRJIg1yZWFkYWJsZQY7AFRJIg9leHBpcmVzX2F0BjsAVDA=--691d627098347705738640552798539681dcd3b6.json",
        "url": "https://3.basecampapi.com/195539477/projects/2085958499.json",
        "app_url": "https://3.basecamp.com/195539477/projects/2085958499",
        "dock": [
            {
                "id": 1069479338,
                "title": "Message Board",
                "name": "message_board",
                "enabled": true,
                "position": 1,
                "url": "https://3.basecampapi.com/195539477/buckets/2085958499/message_boards/1069479338.json",
                "app_url": "https://3.basecamp.com/195539477/buckets/2085958499/message_boards/1069479338"
            },
            {
                "id": 1069479339,
                "title": "To-dos",
                "name": "todoset",
                "enabled": true,
                "position": 2,
                "url": "https://3.basecampapi.com/195539477/buckets/2085958499/todosets/1069479339.json",
                "app_url": "https://3.basecamp.com/195539477/buckets/2085958499/todosets/1069479339"
            },
            {
                "id": 1069479340,
                "title": "Docs & Files",
                "name": "vault",
                "enabled": true,
                "position": 3,
                "url": "https://3.basecampapi.com/195539477/buckets/2085958499/vaults/1069479340.json",
                "app_url": "https://3.basecamp.com/195539477/buckets/2085958499/vaults/1069479340"
            },
            {
                "id": 1069479341,
                "title": "Campfire",
                "name": "chat",
                "enabled": true,
                "position": 4,
                "url": "https://3.basecampapi.com/195539477/buckets/2085958499/chats/1069479341.json",
                "app_url": "https://3.basecamp.com/195539477/buckets/2085958499/chats/1069479341"
            },
            {
                "id": 1069479342,
                "title": "Schedule",
                "name": "schedule",
                "enabled": true,
                "position": 5,
                "url": "https://3.basecampapi.com/195539477/buckets/2085958499/schedules/1069479342.json",
                "app_url": "https://3.basecamp.com/195539477/buckets/2085958499/schedules/1069479342"
            },
            {
                "id": 1069479343,
                "title": "Automatic Check-ins",
                "name": "questionnaire",
                "enabled": false,
                "position": null,
                "url": "https://3.basecampapi.com/195539477/buckets/2085958499/questionnaires/1069479343.json",
                "app_url": "https://3.basecamp.com/195539477/buckets/2085958499/questionnaires/1069479343"
            },
            {
                "id": 1069479344,
                "title": "Email Forwards",
                "name": "inbox",
                "enabled": false,
                "position": null,
                "url": "https://3.basecampapi.com/195539477/buckets/2085958499/inboxes/1069479344.json",
                "app_url": "https://3.basecamp.com/195539477/buckets/2085958499/inboxes/1069479344"
            },
            {
                "id": 1069479345,
                "title": "Card Table",
                "name": "kanban_board",
                "enabled": false,
                "position": null,
                "url": "https://3.basecampapi.com/195539477/buckets/2085958499/card_tables/1069479345.json",
                "app_url": "https://3.basecamp.com/195539477/buckets/2085958499/card_tables/1069479345"
            }
        ]
    }"""
    project = None

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods
        _project = json_loads(cls.project_data)
        _project_dock = _project.pop('dock')  # remove key "dock" from project, later will be used for many-to-many
        _ = BcProject.objects.create(**_project)
        # process many-to-many tools from dock
        for tool in _project_dock:
            try:
                _tool = BcProjectTool.objects.get(id=tool["id"])
            except BcProjectTool.DoesNotExist:
                _tool = BcProjectTool.objects.create(**tool)
            # make sure tool in the project exist
            if not _.dock.filter(id=_tool.id).exists():
                _.dock.add(_tool)

    def setUp(self):  # Run once for every test method to set up clean data
        self.project = json_loads(self.project_data)

    def test_project_id_and_name(self):
        try:
            _project = BcProject.objects.get(id=self.project["id"])
            self.assertEqual(_project.id, self.project["id"])
            self.assertEqual(_project.name, self.project["name"])
            self.assertEqual(_project.purpose, self.project["purpose"])
        except BcProject.DoesNotExist:
            self.fail(msg=f'project with id {self.project["id"]} not found.')

    def test_project_str(self):
        try:
            _project = BcProject.objects.get(id=self.project["id"])
            self.assertEqual(str(_project),
                             f'{self.project["id"]} {self.project["purpose"]} {self.project["name"]}')
        except BcProject.DoesNotExist:
            self.fail(msg=f'project with id {self.project["id"]} not found.')
