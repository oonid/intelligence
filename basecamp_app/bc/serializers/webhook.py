from django.apps import apps as django_apps

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bc.models import BcPeople, BcProject, BcWebhook
from bc.serializers import BcPeopleSerializer
from bc.apps import BcConfig

from copy import deepcopy


class BcWebhookSerializer(serializers.ModelSerializer):
    creator = BcPeopleSerializer()
    recording = None  # GenericForeignKey

    def to_internal_value(self, data):
        """https://www.django-rest-framework.org/api-guide/serializers/#to_internal_valueself-data
        override this method because when overwrite method create, always get exists of creator
        this method called before create, and this override make the creator can use existing
        this method called before is_valid(), so no validated_data
        """
        # for debugging trails, save raw data (before changed below), make copy of data, not only refer to it
        if 'raw' not in data:
            data['raw'] = deepcopy(data)

        # get creator instance from request data
        # can not use db_get_or_create_person as it would be circular import
        try:
            creator = BcPeople.objects.get(id=data["creator"]["id"])
            # assign the creator to serializer
            self.creator = creator
            # remove (pop) the creator field from data if the instance found
            data.pop('creator')
        except BcPeople.DoesNotExist:
            # the creator will be created via BcPeopleSerializer below, now only set as None
            self.creator = None
            # serializer = BcPeopleSerializer(data=creator_data)
            # if serializer.is_valid():
            #     _creator = serializer.save()
            # else:  # invalid serializer
            #     raise ValidationError({"get_or_create_person error": serializer.errors})

        # process recording
        recording_data = data.pop('recording')

        # process bucket inside recording, without proper bucket will return is_valid() as False
        if not ('bucket' in recording_data and recording_data["bucket"]["type"] == "Project"):
            raise ValidationError({"webhook recording bucket error":
                                   f'webhook recording {recording_data["title"]} has no bucket type Project'})

        # can not use utils as it would be circular import
        _recording, _exception = self.get_webhook_recording(recording=recording_data)

        # _recording can be undefined (as it still not saved on db), just skip the process, self.recording as null
        if _recording:
            # recording is a GenericForeignKey
            self.recording = _recording

        # as defined in https://github.com/basecamp/bc3-api/blob/master/sections/webhooks.md
        # The payload for copy/move events will also include some details on the copied recording under "copy"
        # exclude field copy for now, if the key exist
        if 'copy' in data:
            _copy = data.pop('copy')

        # even though the recording exception happened, we did not raise exception, as we just want to save the raw

        return data  # return data without the creator field

    class Meta:
        model = BcWebhook
        fields = '__all__'

    def create(self, validated_data):

        if not self.creator:  # undefined creator, not loaded at to_internal_value()
            creator_data = validated_data.pop('creator')
            creator_serializer = BcPeopleSerializer(data=creator_data)
            if creator_serializer.is_valid():
                self.creator = creator_serializer.save()
            else:  # invalid serializer
                raise ValidationError({"People Serializer error": creator_serializer.errors})

        # process creator and recording to create webhook payload, recording could be None
        payload = BcWebhook.objects.create(creator=self.creator, recording=self.recording, **validated_data)

        return payload

    @staticmethod
    def static_get_webhook_recording_types():
        return ['Comment', 'Document', 'Message', 'Question::Answer', 'Schedule::Entry', 'Todo', 'Todolist', 'Upload',
                'Vault', 'Client::Approval::Response', 'Client::Forward', 'Client::Reply', 'CloudFile',
                'GoogleDocument', 'Inbox::Forward', 'Question']

    @staticmethod
    def static_get_webhook_recording_base_children_types():
        return ["CloudFile", "GoogleDocument", "Inbox::Forward", "Client::Approval::Response", "Client::Forward",
                "Client::Reply"]

    @staticmethod
    def static_get_webhook_recording_type_model_names():
        return {
            'CloudFile': 'BcCloudFile',
            'GoogleDocument': 'BcGoogleDocument',
            'Inbox::Forward': 'BcInboxForward',
            'Client::Approval::Response': 'BcClientApprovalResponse',
            'Client::Forward': 'BcClientForward',
            'Client::Reply': 'BcClientReply',
        }

    @staticmethod
    def static_get_type_model_names():
        return {
            'Comment': 'BcComment',
            'Document': 'BcDocument',
            'Message': 'BcMessage',
            'Question': 'BcQuestion',
            'Question::Answer': 'BcQuestionAnswer',
            'Schedule::Entry': 'BcScheduleEntry',
            'Todo': 'BcTodo',
            'Todolist': 'BcTodolist',
            'Upload': 'BcUpload',
            'Vault': 'BcVault',
        }

    @staticmethod
    def static_get_not_found_message(data):
        return f'{data["type"]} {data["id"]} not found. unable to create new {data["type"]} from data: {data}'

    def get_webhook_recording(self, recording):

        type_model_names = self.static_get_type_model_names()

        if recording["type"] in self.static_get_webhook_recording_base_children_types():

            _recording, _exception = self.get_webhook_recording_base_child(recording=recording)
            if not _recording:  # recording still not recorded on db, create webhook recording base child
                _recording, _exception = self.create_webhook_recording_base_child(recording=recording)

        elif recording["type"] in type_model_names.keys():

            try:
                app_config = django_apps.get_app_config(BcConfig.name)
                app_model = django_apps.get_model(app_label=app_config.name,
                                                  model_name=type_model_names[recording["type"]])
                try:
                    _exception = None  # assign _exception above _recording to comply the coverage :)
                    _recording = app_model.objects.get(id=recording["id"])
                except app_model.DoesNotExist:
                    _recording = None
                    _exception = self.static_get_not_found_message(recording)
            except LookupError:
                _recording = None
                _exception = f'model not found for recording type {recording["type"]}'

        else:
            _recording = None
            _exception = (f'recording {recording["id"]} type {recording["type"]} not in '
                          f'{self.static_get_webhook_recording_types()}')

        return _recording, _exception

    def get_webhook_parent(self, parent):
        if not parent:  # None
            return None, f'webhook recording has no parent'

        type_model_names = self.static_get_type_model_names()

        if parent["type"] not in type_model_names.keys():
            return None, f'webhook recording parent type unknown: {parent["type"]}'

        try:
            app_config = django_apps.get_app_config(BcConfig.name)
            app_model = django_apps.get_model(app_label=app_config.name,
                                              model_name=type_model_names[parent["type"]])
            try:
                _exception = None  # assign _exception above _parent to comply the coverage :)
                _parent = app_model.objects.get(id=parent["id"])
            except app_model.DoesNotExist:
                _parent = None
                _exception = self.static_get_not_found_message(parent)
        except LookupError:
            _parent = None
            _exception = f'model not found for parent type {parent["type"]}'

        return _parent, _exception

    def get_recording_bucket(self, bucket):
        if not bucket:  # None
            return None, f'webhook recording has no bucket'

        if not bucket["type"] == "Project":
            return None, f'webhook recording has no bucket type Project'

        try:
            _bucket = BcProject.objects.get(id=bucket["id"])
            _exception = None
        except BcProject.DoesNotExist:
            # can not create BcProject from very limited data of recording bucket
            _bucket = None
            _exception = self.static_get_not_found_message(data=bucket)

        return _bucket, _exception

    @staticmethod
    def get_or_create_recording_creator(creator):
        if not creator:  # None
            return None, f'webhook recording has no creator'

        # can not use db_get_or_create_person as it would be circular import
        try:
            _creator = BcPeople.objects.get(id=creator["id"])
            _exception = None
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=creator)
            if serializer.is_valid():
                _creator = serializer.save()
                _exception = None
            else:  # invalid serializer
                _creator = None
                _exception = f'get_or_create_person error: {serializer.errors}'

        return _creator, _exception

    def get_webhook_recording_base_child(self, recording):
        type_model_names = self.static_get_webhook_recording_type_model_names()

        if recording["type"] in self.static_get_webhook_recording_base_children_types():
            try:
                app_config = django_apps.get_app_config(BcConfig.name)
                app_model = django_apps.get_model(app_label=app_config.name,
                                                  model_name=type_model_names[recording["type"]])
                try:
                    _exception = None  # assign _exception above _recording to comply the coverage :)
                    _recording = app_model.objects.get(id=recording["id"])
                except app_model.DoesNotExist:
                    _recording = None
                    _exception = self.static_get_not_found_message(recording)
            except LookupError:
                _recording = None
                _exception = f'model not found for recording type {recording["type"]}'

        else:
            _recording = None
            _exception = (f'recording {recording["id"]} type {recording["type"]} not in '
                          f'{self.static_get_webhook_recording_base_children_types()}')

        return _recording, _exception

    def _create_webhook_recording_base_child_model(self, recording, _bucket, _creator, _parent):
        """
        make sure all parameters not None.
        make sure this method only called by create_webhook_recording_base_child().
        split this method to set easier on test.
        :param recording:
        :param _bucket:
        :param _creator:
        :param _parent:
        :return:
        """

        if recording["type"] in self.static_get_webhook_recording_base_children_types():
            type_model_names = self.static_get_webhook_recording_type_model_names()
            try:
                app_config = django_apps.get_app_config(BcConfig.name)
                app_model = django_apps.get_model(app_label=app_config.name,
                                                  model_name=type_model_names[recording["type"]])
                _recording = app_model.objects.create(bucket=_bucket, creator=_creator, parent=_parent, **recording)
                _exception = None
            except LookupError:
                _recording = None
                _exception = f'model not found for recording type {recording["type"]}'

        else:
            _recording = None
            _exception = (f'recording {recording["id"]} type {recording["type"]} not in '
                          f'{self.static_get_webhook_recording_base_children_types()}')

        return _recording, _exception

    def create_webhook_recording_base_child(self, recording):
        # to create a child of BcWebhookRecordingBase, it needs: bucket, creator, parent.

        bucket_data = recording.pop('bucket', None)
        _bucket, _exception = self.get_recording_bucket(bucket=bucket_data)
        if not _bucket:
            return None, _exception

        # create or get creator instance from request data, remove (pop) the creator field from data
        creator_data = recording.pop('creator', None)
        _creator, _exception = self.get_or_create_recording_creator(creator=creator_data)
        if not _creator:
            return None, _exception

        # process variant of parents
        parent_data = recording.pop('parent', None)
        _parent, _exception = self.get_webhook_parent(parent=parent_data)
        if not _parent:
            return None, _exception

        _recording, _exception = self._create_webhook_recording_base_child_model(
            recording=recording, _bucket=_bucket, _creator=_creator, _parent=_parent)

        return _recording, _exception
