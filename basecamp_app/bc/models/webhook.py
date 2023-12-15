from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from bc.models import BcPeople, BcProject


class BcWebhookRecordingBase(models.Model):
    id = models.BigIntegerField(primary_key=True)  # Basecamp Webhook Recording (base) ID
    status = models.CharField(max_length=30)
    visible_to_clients = models.BooleanField()
    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField()
    title = models.CharField(max_length=100)
    inherits_status = models.BooleanField()
    type = models.CharField(max_length=30)
    url = models.URLField()
    app_url = models.URLField()
    bookmark_url = models.URLField()
    subscription_url = models.URLField()
    position = models.IntegerField(null=True)
    parent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_object_id = models.PositiveIntegerField()
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    parent = GenericForeignKey("parent_content_type", "parent_object_id")
    bucket = models.ForeignKey(to=BcProject, on_delete=models.CASCADE)
    creator = models.ForeignKey(to=BcPeople, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        abstract = True


class BcCloudFile(BcWebhookRecordingBase):
    """
    CloudFile is one of the endpoints in webhooks.
    no specific definition of CloudFile in the documentation,
    so let's start with fields from webhooks recording.
    https://github.com/basecamp/bc3-api/blob/master/sections/webhooks.md
    """
    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'


class BcGoogleDocument(BcWebhookRecordingBase):
    """
    GoogleDocument is one of the endpoints in webhooks.
    no specific definition of GoogleDocument in the documentation,
    so let's start with fields from webhooks recording.
    https://github.com/basecamp/bc3-api/blob/master/sections/webhooks.md
    """
    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'


class BcInboxForward(BcWebhookRecordingBase):
    """
    InboxForward is one of the endpoints in webhooks.
    TODO: move InboxForward from webhook
    https://github.com/basecamp/bc3-api/blob/master/sections/forwards.md#get-a-forward
    """


class BcClientApprovalResponse(BcWebhookRecordingBase):
    """
    ClientApprovalResponse is one of the endpoints in webhooks.
    TODO: move ClientApprovalResponse from webhook
    https://github.com/basecamp/bc3-api/blob/master/sections/client_approvals.md#get-a-client-approval
    """


class BcClientForward(BcWebhookRecordingBase):
    """
    ClientForward is one of the endpoints in webhooks.
    no specific definition of ClientForward in the documentation,
    so let's start with fields from webhooks recording.
    https://github.com/basecamp/bc3-api/blob/master/sections/webhooks.md
    need sample data for ClientForward
    """


class BcClientReply(BcWebhookRecordingBase):
    """
    ClientReply is one of the endpoints in webhooks.
    TODO: move ClientReply from webhook
    https://github.com/basecamp/bc3-api/blob/master/sections/client_replies.md#get-client-replies
    """


class BcWebhook(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/webhooks.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Webhook ID
    created_at = models.DateTimeField(db_index=True)
    kind = models.CharField(max_length=100)
    # structure for details still too broad. e.g.: {}
    # { "notified_recipient_ids": [1007299144] }
    # { "copy_id": 981721240 }
    # { "added_person_ids": [36997868], "removed_person_ids": [] }
    # { "status_was": "trashed" }
    details = models.JSONField(null=True, blank=True)
    creator = models.ForeignKey(to=BcPeople, on_delete=models.CASCADE)
    # recording can be undefined if part of it still unavailable at db. set null & blank at these two.
    recording_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    recording_object_id = models.PositiveIntegerField(null=True, blank=True)
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    recording = GenericForeignKey("recording_content_type", "recording_object_id")
    # record raw data for debugging trails, especially if the recording still undefined (null)
    raw = models.JSONField()

    def __str__(self):
        return f'webhook {self.id} {self.kind}'
