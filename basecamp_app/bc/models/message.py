from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from bc.models import BcPeople, BcProject


class BcMessageCategory(models.Model):
    """
    field category of message, also called message types
    https://github.com/basecamp/bc3-api/blob/master/sections/message_types.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Message Category ID
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=30)
    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField()

    def __str__(self):
        return f'message category {self.id} {self.name})'


class BcMessageBoard(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/message_boards.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Message Board ID
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
    position = models.IntegerField(null=True)
    bucket = models.ForeignKey(to=BcProject, on_delete=models.CASCADE)
    creator = models.ForeignKey(to=BcPeople, on_delete=models.CASCADE)
    messages_count = models.IntegerField()
    messages_url = models.URLField()
    app_messages_url = models.URLField()

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'


class BcMessage(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/messages.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Message ID
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
    comments_count = models.IntegerField()
    comments_url = models.URLField()
    # parent in ["Message::Board"]
    parent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_object_id = models.PositiveIntegerField()
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    parent = GenericForeignKey("parent_content_type", "parent_object_id")
    bucket = models.ForeignKey(to=BcProject, on_delete=models.CASCADE)
    creator = models.ForeignKey(to=BcPeople, on_delete=models.CASCADE)
    content = models.TextField()
    category = models.ForeignKey(to=BcMessageCategory, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'
