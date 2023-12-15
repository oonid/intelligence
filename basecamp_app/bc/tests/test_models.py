from django.test import TestCase

from pathlib import Path
from json import loads as json_loads, dumps as json_dumps, load as json_stream_load

from bc.models import (BcCompany, BcPeople, BcProjectTool, BcProject, BcQuestionnaire, BcQuestion,
                       BcQuestionAnswer, BcSchedule, BcScheduleEntry, BcTodoset, BcTodolist, BcTodo,
                       BcMessageCategory, BcMessageBoard, BcMessage, BcVault, BcDocument, BcUpload, BcComment,
                       BcWebhook)


class MultiModelsTest(TestCase):
    # load initial data for these tests
    fixtures = ["bc_bccompany", "bc_bcpeople", "bc_bcproject", "bc_bcprojecttool",
                "bc_bcquestionnaire", "bc_bcquestion", "bc_bcquestionanswer", "bc_bcrecurrenceschedule",
                "bc_bcschedule", "bc_bcscheduleentry",
                "bc_bcmessagecategory", "bc_bcmessageboard", "bc_bcmessage",
                "bc_bctodoset", "bc_bctodolist", "bc_bctodo", "bc_bctodocompletion",
                "bc_bcvault", "bc_bcdocument", "bc_bcupload",
                "bc_bccomment", "bc_bcwebhook", "bc_bccloudfile", "bc_bcgoogledocument"]

    @classmethod
    def setUpTestData(cls):  # Run once to set up non-modified data for all class methods

        # api_sample.json is collections of API data from bc3-api site https://github.com/basecamp/bc3-api/tree/master
        test_dir = Path(__file__).resolve().parent
        with open(test_dir / "api_sample.json") as stream:
            api_sample_json = json_stream_load(stream)

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/people.md
        # the database loaded with fixture bc_bcpeople.json and bc_bccompany.json
        cls.person_data = json_dumps(api_sample_json["person"]["1049715914"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/projects.md#get-a-project
        # the database loaded with fixture bc_bcproject.json and bc_bcprojecttool.json
        cls.project_data = json_dumps(api_sample_json["project"]["2085958499"])

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/questionnaires.md#get-questionnaire
        # the database loaded with fixture bc_bcquestionnaire.json
        cls.questionnaire_data = json_dumps(api_sample_json["questionnaire"]["1069479343"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/questions.md#get-a-question
        # the database loaded with fixture bc_bcquestion.json and bc_bcrecurrenceschedule.json
        cls.question_data = json_dumps(api_sample_json["question"]["1069479362"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/question_answers.md
        # the database loaded with fixture bc_bcquestionanswer.json
        cls.question_answer_data = json_dumps(api_sample_json["question_answer"]["1069479547"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/schedules.md#get-schedule
        # the database loaded with fixture bc_bcschedule.json
        cls.schedule_data = json_dumps(api_sample_json["schedule"]["1069479342"])

        # sample from https://github.com/basecamp/bc3-api/blob/master/sections/schedule_entries.md#get-a-schedule-entry
        # the database loaded with fixture bc_bcscheduleentry.json
        cls.schedule_entry_data = json_dumps(api_sample_json["schedule_entry"]["1069479847"])

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/todosets.md
        # the database loaded with fixture bc_bctodoset.json
        cls.todoset_data = json_dumps(api_sample_json["todoset"]["1069479339"])

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/todolists.md#example-json-response
        # the database loaded with fixture bc_bctodolist.json
        cls.todolist_data = json_dumps(api_sample_json["todolist"]["1069479520"])

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/todos.md#get-a-to-do
        # the database loaded with fixture bc_bctodo.json
        cls.todo_data = json_dumps(api_sample_json["todo"]["1069479523"])

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md#get-a-message-type
        # the database loaded with fixture bc_bcmessagecategory.json
        cls.message_category_data = json_dumps(api_sample_json["message_category"]["823758531"])

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/message_boards.md#get-message-board
        # the database loaded with fixture bc_bcmessageboard.json
        cls.message_board_data = json_dumps(api_sample_json["message_board"]["1069479338"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/messages.md#get-a-message
        # the database loaded with fixture bc_bcmessage.json
        cls.message_data = json_dumps(api_sample_json["message"]["1069479351"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/vaults.md#get-a-vault
        # using vault with ID 1069479098, generated from Document below (1069479093) as dummy data
        # the database loaded with fixture bc_bcvault.json
        cls.vault_1069479098_data = json_dumps(api_sample_json["vault"]["1069479098"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/documents.md
        # the database loaded with fixture bc_bcdocument.json
        cls.document_data = json_dumps(api_sample_json["document"]["1069479093"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/uploads.md#get-an-upload
        # the database loaded with fixture bc_bcupload.json
        cls.upload_data = json_dumps(api_sample_json["upload"]["1069479848"])

        # sample API data from https://github.com/basecamp/bc3-api/blob/master/sections/comments.md#get-a-comment
        # the database loaded with fixture bc_bccomment.json
        cls.comment_data = json_dumps(api_sample_json["comment"]["1069479361"])

        # sample data from https://github.com/basecamp/bc3-api/blob/master/sections/webhooks.md
        # change the project id 68833643212 to 2085958499 (Project The Leto Laptop, as defined above)
        # the database loaded with fixture bc_bcwebhook.json
        cls.webhook_data = json_dumps(api_sample_json["webhook"]["1479523571"])

        # webhook with recording type CloudFile using dummy data
        # the database loaded with fixture bc_bccloudfile.json
        cls.webhook_cloudfile_data = json_dumps(api_sample_json["webhook"]["1479523572"])

        # webhook with recording type GoogleDocument using dummy data
        # the database loaded with fixture bc_bcgoogledocument.json
        cls.webhook_googledocument_data = json_dumps(api_sample_json["webhook"]["1479523573"])

        # _webhook_googledocument = api_sample_json["webhook"]["1479523573"]
        # _webhook_googledocument['raw'] = deepcopy(_webhook_googledocument)
        # _webhook_googledocument_creator = _webhook_googledocument.pop('creator')
        # _webhook_creator = BcPeople.objects.get(id=_webhook_googledocument_creator["id"])
        # _webhook_googledocument_recording = _webhook_googledocument.pop('recording')
        #
        # _webhook_googledocument_recording_bucket = _webhook_googledocument_recording.pop('bucket')
        # _recording_bucket = BcProject.objects.get(id=_webhook_googledocument_recording_bucket["id"])
        # _webhook_googledocument_recording_creator = _webhook_googledocument_recording.pop('creator')
        # _recording_creator = BcPeople.objects.get(id=_webhook_googledocument_recording_creator["id"])
        # _recording_parent = _webhook_googledocument_recording.pop('parent')
        # _recording_vault = BcVault.objects.get(id=_recording_parent["id"])
        #
        # _recording = BcGoogleDocument.objects.create(bucket=_recording_bucket, creator=_recording_creator,
        #                                              parent=_recording_vault, **_webhook_googledocument_recording)
        #
        # # create BcWebhook after recording ready
        # _ = BcWebhook.objects.create(creator=_webhook_creator, recording=_recording, **_webhook_googledocument)
        #
        #
        # # dump data from loaded process above
        # management.call_command('dumpdata', 'bc.BcWebhook', natural_foreign=True,
        #                         output="bc/fixtures/bc_bcwebhook.json")
        # management.call_command('dumpdata', 'bc.BcGoogleDocument', natural_foreign=True,
        #                         output="bc/fixtures/bc_bcgoogledocument.json")

    def setUp(self):  # Run once for every test method to set up clean data
        self.person = json_loads(self.person_data)
        self.company = self.person['company']
        self.project = json_loads(self.project_data)
        self.questionnaire = json_loads(self.questionnaire_data)
        self.question = json_loads(self.question_data)
        self.question_answer = json_loads(self.question_answer_data)
        self.schedule = json_loads(self.schedule_data)
        self.schedule_entry = json_loads(self.schedule_entry_data)
        self.todoset = json_loads(self.todoset_data)
        self.todolist = json_loads(self.todolist_data)
        self.todo = json_loads(self.todo_data)
        self.message_category = json_loads(self.message_category_data)
        self.message_board = json_loads(self.message_board_data)
        self.message = json_loads(self.message_data, strict=False)  # disable strict to process content with \n
        self.vault = json_loads(self.vault_1069479098_data)
        self.document = json_loads(self.document_data, strict=False)  # disable strict to process content with \n
        self.upload = json_loads(self.upload_data)
        self.comment = json_loads(self.comment_data)
        self.webhook = json_loads(self.webhook_data)
        self.webhook_cloudfile = json_loads(self.webhook_cloudfile_data)
        self.webhook_googledocument = json_loads(self.webhook_googledocument_data)

    def test_company_id_and_name(self):
        try:
            _company = BcCompany.objects.get(id=self.company["id"])
            self.assertEqual(_company.id, self.company["id"])
            self.assertEqual(_company.name, self.company["name"])
        except BcCompany.DoesNotExist:
            self.fail(msg=f'company with id {self.company["id"]} not found.')

    def test_company_str(self):
        try:
            _company = BcCompany.objects.get(id=self.company["id"])
            self.assertEqual(str(_company), f'{self.company["id"]} {self.company["name"]}')
        except BcCompany.DoesNotExist:
            self.fail(msg=f'company with id {self.company["id"]} not found.')

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

    def test_project_tool_id_and_name(self):
        _project_dock = self.project["dock"]
        if len(_project_dock) > 0:
            _project_tool = _project_dock[0]
        else:
            self.fail(msg=f'project with id {self.project["id"]} has no docks data.')

        try:
            _project = BcProject.objects.get(id=self.project["id"])

            if _project.dock.count() > 0:
                _tool = _project.dock.first()
            else:
                self.fail(msg=f'project with id {self.project["id"]} has no docks.')

            self.assertEqual(_tool.id, _project_tool["id"])
            self.assertEqual(_tool.name, _project_tool["name"])
            self.assertEqual(_tool.title, _project_tool["title"])
            self.assertEqual(_tool.enabled, _project_tool["enabled"])
        except BcProjectTool.DoesNotExist:
            self.fail(msg=f'tool with id {_project_tool["id"]} not found.')

    def test_project_tool_str(self):
        _project_dock = self.project["dock"]
        if len(_project_dock) > 0:
            _project_tool = _project_dock[0]
        else:
            self.fail(msg=f'project with id {self.project["id"]} has no docks data.')

        try:
            _project = BcProject.objects.get(id=self.project["id"])

            if _project.dock.count() > 0:
                _tool = _project.dock.first()
            else:
                self.fail(msg=f'project with id {self.project["id"]} has no docks.')

            self.assertEqual(str(_tool),
                             f'{_project_tool["id"]} {_project_tool["name"]} {_project_tool["title"]} '
                             f'({_project_tool["enabled"]})')
        except BcProjectTool.DoesNotExist:
            self.fail(msg=f'tool with id {_project_tool["id"]} not found.')

    def test_questionnaire_id_and_title(self):
        try:
            _questionnaire = BcQuestionnaire.objects.get(id=self.questionnaire["id"])
            self.assertEqual(_questionnaire.id, self.questionnaire["id"])
            self.assertEqual(_questionnaire.type, self.questionnaire["type"])
            self.assertEqual(_questionnaire.title, self.questionnaire["title"])
            self.assertEqual(_questionnaire.status, self.questionnaire["status"])
        except BcQuestionnaire.DoesNotExist:
            self.fail(msg=f'questionnaire with id {self.questionnaire["id"]} not found.')

    def test_questionnaire_str(self):
        try:
            _questionnaire = BcQuestionnaire.objects.get(id=self.questionnaire["id"])
            self.assertEqual(str(_questionnaire),
                             f'{self.questionnaire["type"]} {self.questionnaire["id"]} {self.questionnaire["title"]} '
                             f'({self.questionnaire["status"]})')
        except BcQuestionnaire.DoesNotExist:
            self.fail(msg=f'questionnaire with id {self.questionnaire["id"]} not found.')

    def test_question_id_and_title(self):
        try:
            _question = BcQuestion.objects.get(id=self.question["id"])
            self.assertEqual(_question.id, self.question["id"])
            self.assertEqual(_question.type, self.question["type"])
            self.assertEqual(_question.title, self.question["title"])
            self.assertEqual(_question.status, self.question["status"])
        except BcQuestion.DoesNotExist:
            self.fail(msg=f'question with id {self.question["id"]} not found.')

    def test_question_str(self):
        try:
            _question = BcQuestion.objects.get(id=self.question["id"])
            self.assertEqual(str(_question),
                             f'{self.question["type"]} {self.question["id"]} {self.question["title"]} '
                             f'({self.question["status"]})')
        except BcQuestion.DoesNotExist:
            self.fail(msg=f'question with id {self.question["id"]} not found.')

    def test_question_schedule_str(self):
        try:
            _question = BcQuestion.objects.get(id=self.question["id"])
            _question_schedule = self.question["schedule"]
            self.assertEqual(str(_question.schedule),
                             f'{_question_schedule["frequency"]} starts at {_question_schedule["start_date"]}')
        except BcQuestion.DoesNotExist:
            self.fail(msg=f'question with id {self.question["id"]} not found.')

    def test_question_answer_id_and_title(self):
        try:
            _question_answer = BcQuestionAnswer.objects.get(id=self.question_answer["id"])
            self.assertEqual(_question_answer.id, self.question_answer["id"])
            self.assertEqual(_question_answer.type, self.question_answer["type"])
            self.assertEqual(_question_answer.title, self.question_answer["title"])
            self.assertEqual(_question_answer.status, self.question_answer["status"])
        except BcQuestionAnswer.DoesNotExist:
            self.fail(msg=f'question answer with id {self.question_answer["id"]} not found.')

    def test_question_answer_str(self):
        try:
            _question = BcQuestionAnswer.objects.get(id=self.question_answer["id"])
            self.assertEqual(str(_question),
                             f'{self.question_answer["type"]} {self.question_answer["id"]} '
                             f'{self.question_answer["title"]} ({self.question_answer["status"]})')
        except BcQuestionAnswer.DoesNotExist:
            self.fail(msg=f'question answer with id {self.question_answer["id"]} not found.')

    def test_schedule_id_and_title(self):
        try:
            _schedule = BcSchedule.objects.get(id=self.schedule["id"])
            self.assertEqual(_schedule.id, self.schedule["id"])
            self.assertEqual(_schedule.type, self.schedule["type"])
            self.assertEqual(_schedule.title, self.schedule["title"])
            self.assertEqual(_schedule.status, self.schedule["status"])
        except BcSchedule.DoesNotExist:
            self.fail(msg=f'schedule with id {self.schedule["id"]} not found.')

    def test_schedule_str(self):
        try:
            _schedule = BcSchedule.objects.get(id=self.schedule["id"])
            self.assertEqual(str(_schedule),
                             f'{self.schedule["type"]} {self.schedule["id"]} {self.schedule["title"]} '
                             f'({self.schedule["status"]})')
        except BcSchedule.DoesNotExist:
            self.fail(msg=f'schedule with id {self.schedule["id"]} not found.')

    def test_schedule_entry_id_and_title(self):
        try:
            _schedule_entry = BcScheduleEntry.objects.get(id=self.schedule_entry["id"])
            self.assertEqual(_schedule_entry.id, self.schedule_entry["id"])
            self.assertEqual(_schedule_entry.type, self.schedule_entry["type"])
            self.assertEqual(_schedule_entry.title, self.schedule_entry["title"])
            self.assertEqual(_schedule_entry.status, self.schedule_entry["status"])
        except BcScheduleEntry.DoesNotExist:
            self.fail(msg=f'schedule with id {self.schedule["id"]} not found.')

    def test_schedule_entry_str(self):
        try:
            _schedule_entry = BcScheduleEntry.objects.get(id=self.schedule_entry["id"])
            self.assertEqual(str(_schedule_entry),
                             f'{self.schedule_entry["type"]} {self.schedule_entry["id"]} '
                             f'{self.schedule_entry["title"]} ({self.schedule_entry["status"]})')
        except BcScheduleEntry.DoesNotExist:
            self.fail(msg=f'schedule entry with id {self.schedule_entry["id"]} not found.')

    def test_todoset_id_and_title(self):
        try:
            _todoset = BcTodoset.objects.get(id=self.todoset["id"])
            self.assertEqual(_todoset.id, self.todoset["id"])
            self.assertEqual(_todoset.type, self.todoset["type"])
            self.assertEqual(_todoset.title, self.todoset["title"])
            self.assertEqual(_todoset.status, self.todoset["status"])
        except BcTodoset.DoesNotExist:
            self.fail(msg=f'todoset with id {self.todoset["id"]} not found.')

    def test_todoset_str(self):
        try:
            _todoset = BcTodoset.objects.get(id=self.todoset["id"])
            self.assertEqual(str(_todoset),
                             f'{self.todoset["type"]} {self.todoset["id"]} {self.todoset["title"]} '
                             f'({self.todoset["status"]})')
        except BcTodoset.DoesNotExist:
            self.fail(msg=f'todoset with id {self.todoset["id"]} not found.')

    def test_todolist_id_and_title(self):
        try:
            _todolist = BcTodolist.objects.get(id=self.todolist["id"])
            self.assertEqual(_todolist.id, self.todolist["id"])
            self.assertEqual(_todolist.type, self.todolist["type"])
            self.assertEqual(_todolist.title, self.todolist["title"])
            self.assertEqual(_todolist.status, self.todolist["status"])
        except BcTodolist.DoesNotExist:
            self.fail(msg=f'todolist with id {self.todolist["id"]} not found.')

    def test_todolist_str(self):
        try:
            _todolist = BcTodolist.objects.get(id=self.todolist["id"])
            self.assertEqual(str(_todolist),
                             f'{self.todolist["type"]} {self.todolist["id"]} {self.todolist["title"]} '
                             f'({self.todolist["status"]})')
        except BcTodolist.DoesNotExist:
            self.fail(msg=f'todolist with id {self.todolist["id"]} not found.')

    def test_todo_id_and_title(self):
        try:
            _todo = BcTodo.objects.get(id=self.todo["id"])
            self.assertEqual(_todo.id, self.todo["id"])
            self.assertEqual(_todo.type, self.todo["type"])
            self.assertEqual(_todo.title, self.todo["title"])
            self.assertEqual(_todo.status, self.todo["status"])
        except BcTodo.DoesNotExist:
            self.fail(msg=f'todo with id {self.todo["id"]} not found.')

    def test_todo_str(self):
        try:
            _todo = BcTodo.objects.get(id=self.todo["id"])
            self.assertEqual(str(_todo),
                             f'{self.todo["type"]} {self.todo["id"]} {self.todo["title"]} '
                             f'({self.todo["status"]})')
        except BcTodo.DoesNotExist:
            self.fail(msg=f'todo with id {self.todo["id"]} not found.')

    def test_message_category_id_and_name(self):
        try:
            _message_category = BcMessageCategory.objects.get(id=self.message_category["id"])
            self.assertEqual(_message_category.id, self.message_category["id"])
            self.assertEqual(_message_category.name, self.message_category["name"])
        except BcMessageCategory.DoesNotExist:
            self.fail(msg=f'message category with id {self.message_category["id"]} not found.')

    def test_message_category_str(self):
        try:
            _message_category = BcMessageCategory.objects.get(id=self.message_category["id"])
            self.assertEqual(str(_message_category),
                             f'message category {self.message_category["id"]} {self.message_category["name"]}')
        except BcMessageCategory.DoesNotExist:
            self.fail(msg=f'message category with id {self.message_category["id"]} not found.')

    def test_message_board_id_and_title(self):
        try:
            _message_board = BcMessageBoard.objects.get(id=self.message_board["id"])
            self.assertEqual(_message_board.id, self.message_board["id"])
            self.assertEqual(_message_board.type, self.message_board["type"])
            self.assertEqual(_message_board.title, self.message_board["title"])
            self.assertEqual(_message_board.status, self.message_board["status"])
        except BcMessageBoard.DoesNotExist:
            self.fail(msg=f'message board with id {self.message_board["id"]} not found.')

    def test_message_board_str(self):
        try:
            _message_board = BcMessageBoard.objects.get(id=self.message_board["id"])
            self.assertEqual(str(_message_board), f'{self.message_board["type"]} {self.message_board["id"]} '
                                                  f'{self.message_board["title"]} ({self.message_board["status"]})')
        except BcMessageBoard.DoesNotExist:
            self.fail(msg=f'message board with id {self.message_board["id"]} not found.')

    def test_message_id_and_title(self):
        try:
            _message = BcMessage.objects.get(id=self.message["id"])
            self.assertEqual(_message.id, self.message["id"])
            self.assertEqual(_message.type, self.message["type"])
            self.assertEqual(_message.title, self.message["title"])
            self.assertEqual(_message.status, self.message["status"])
        except BcMessage.DoesNotExist:
            self.fail(msg=f'message with id {self.message["id"]} not found.')

    def test_message_str(self):
        try:
            _message = BcMessage.objects.get(id=self.message["id"])
            self.assertEqual(str(_message), f'{self.message["type"]} {self.message["id"]} '
                                            f'{self.message["title"]} ({self.message["status"]})')
        except BcMessage.DoesNotExist:
            self.fail(msg=f'message with id {self.message["id"]} not found.')

    def test_vault_id_and_title(self):
        try:
            _vault = BcVault.objects.get(id=self.vault["id"])
            self.assertEqual(_vault.id, self.vault["id"])
            self.assertEqual(_vault.type, self.vault["type"])
            self.assertEqual(_vault.title, self.vault["title"])
            self.assertEqual(_vault.status, self.vault["status"])
        except BcVault.DoesNotExist:
            self.fail(msg=f'vault with id {self.vault["id"]} not found.')

    def test_vault_str(self):
        try:
            _vault = BcVault.objects.get(id=self.vault["id"])
            self.assertEqual(str(_vault), f'{self.vault["type"]} {self.vault["id"]} '
                                          f'{self.vault["title"]} ({self.vault["status"]})')
        except BcVault.DoesNotExist:
            self.fail(msg=f'vault with id {self.vault["id"]} not found.')

    def test_document_id_and_title(self):
        try:
            _document = BcDocument.objects.get(id=self.document["id"])
            self.assertEqual(_document.id, self.document["id"])
            self.assertEqual(_document.type, self.document["type"])
            self.assertEqual(_document.title, self.document["title"])
            self.assertEqual(_document.status, self.document["status"])
        except BcDocument.DoesNotExist:
            self.fail(msg=f'document with id {self.document["id"]} not found.')

    def test_document_str(self):
        try:
            _document = BcDocument.objects.get(id=self.document["id"])
            self.assertEqual(str(_document), f'{self.document["type"]} {self.document["id"]} '
                                             f'{self.document["title"]} ({self.document["status"]})')
        except BcDocument.DoesNotExist:
            self.fail(msg=f'document with id {self.document["id"]} not found.')

    def test_upload_id_and_title(self):
        try:
            _upload = BcUpload.objects.get(id=self.upload["id"])
            self.assertEqual(_upload.id, self.upload["id"])
            self.assertEqual(_upload.type, self.upload["type"])
            self.assertEqual(_upload.title, self.upload["title"])
            self.assertEqual(_upload.status, self.upload["status"])
        except BcUpload.DoesNotExist:
            self.fail(msg=f'upload with id {self.upload["id"]} not found.')

    def test_upload_str(self):
        try:
            _upload = BcUpload.objects.get(id=self.upload["id"])
            self.assertEqual(str(_upload), f'{self.upload["type"]} {self.upload["id"]} '
                                           f'{self.upload["title"]} ({self.upload["status"]})')
        except BcUpload.DoesNotExist:
            self.fail(msg=f'upload with id {self.upload["id"]} not found.')

    def test_comment_id_and_title(self):
        try:
            _comment = BcComment.objects.get(id=self.comment["id"])
            self.assertEqual(_comment.id, self.comment["id"])
            self.assertEqual(_comment.type, self.comment["type"])
            self.assertEqual(_comment.title, self.comment["title"])
            self.assertEqual(_comment.status, self.comment["status"])
        except BcComment.DoesNotExist:
            self.fail(msg=f'message with id {self.comment["id"]} not found.')

    def test_comment_str(self):
        try:
            _comment = BcComment.objects.get(id=self.comment["id"])
            self.assertEqual(str(_comment), f'{self.comment["type"]} {self.comment["id"]} '
                                            f'{self.comment["title"]} ({self.comment["status"]})')
        except BcComment.DoesNotExist:
            self.fail(msg=f'message with id {self.comment["id"]} not found.')

    def test_webhook_id_and_kind(self):
        try:
            _webhook = BcWebhook.objects.get(id=self.webhook["id"])
            self.assertEqual(_webhook.id, self.webhook["id"])
            self.assertEqual(_webhook.kind, self.webhook["kind"])
        except BcWebhook.DoesNotExist:
            self.fail(msg=f'webhook with id {self.webhook["id"]} not found.')

    def test_webhook_str(self):
        try:
            _webhook = BcWebhook.objects.get(id=self.webhook["id"])
            self.assertEqual(str(_webhook), f'webhook {self.webhook["id"]} {self.webhook["kind"]}')
        except BcWebhook.DoesNotExist:
            self.fail(msg=f'webhook with id {self.webhook["id"]} not found.')

    def test_webhook_cloudfile_id_and_title(self):
        try:
            _webhook = BcWebhook.objects.get(id=self.webhook_cloudfile["id"])
            self.assertEqual(_webhook.id, self.webhook_cloudfile["id"])
            self.assertEqual(_webhook.kind, self.webhook_cloudfile["kind"])

            # test recording of webhook, type CloudFile
            self.assertEqual(_webhook.recording.type, "CloudFile")
            self.assertEqual(_webhook.recording.type, self.webhook_cloudfile["recording"]["type"])
            self.assertEqual(_webhook.recording.id, self.webhook_cloudfile["recording"]["id"])
            self.assertEqual(_webhook.recording.title, self.webhook_cloudfile["recording"]["title"])
            self.assertEqual(_webhook.recording.status, self.webhook_cloudfile["recording"]["status"])

        except BcWebhook.DoesNotExist:
            self.fail(msg=f'webhook with id {self.webhook["id"]} not found.')

    def test_webhook_cloudfile_str(self):
        try:
            _webhook = BcWebhook.objects.get(id=self.webhook_cloudfile["id"])

            # test webhook recording string representation
            self.assertEqual(str(_webhook.recording), f'{self.webhook_cloudfile["recording"]["type"]} '
                                                      f'{self.webhook_cloudfile["recording"]["id"]} '
                                                      f'{self.webhook_cloudfile["recording"]["title"]} '
                                                      f'({self.webhook_cloudfile["recording"]["status"]})')

        except BcWebhook.DoesNotExist:
            self.fail(msg=f'webhook with id {self.webhook["id"]} not found.')

    def test_webhook_googledocument_id_and_title(self):
        try:
            _webhook = BcWebhook.objects.get(id=self.webhook_googledocument["id"])
            self.assertEqual(_webhook.id, self.webhook_googledocument["id"])
            self.assertEqual(_webhook.kind, self.webhook_googledocument["kind"])

            # test recording of webhook, type GoogleDocument
            self.assertEqual(_webhook.recording.type, "GoogleDocument")
            self.assertEqual(_webhook.recording.type, self.webhook_googledocument["recording"]["type"])
            self.assertEqual(_webhook.recording.id, self.webhook_googledocument["recording"]["id"])
            self.assertEqual(_webhook.recording.title, self.webhook_googledocument["recording"]["title"])
            self.assertEqual(_webhook.recording.status, self.webhook_googledocument["recording"]["status"])

        except BcWebhook.DoesNotExist:
            self.fail(msg=f'webhook with id {self.webhook["id"]} not found.')

    def test_webhook_googledocument_str(self):
        try:
            _webhook = BcWebhook.objects.get(id=self.webhook_googledocument["id"])

            # test webhook recording string representation
            self.assertEqual(str(_webhook.recording), f'{self.webhook_googledocument["recording"]["type"]} '
                                                      f'{self.webhook_googledocument["recording"]["id"]} '
                                                      f'{self.webhook_googledocument["recording"]["title"]} '
                                                      f'({self.webhook_googledocument["recording"]["status"]})')

        except BcWebhook.DoesNotExist:
            self.fail(msg=f'webhook with id {self.webhook["id"]} not found.')
