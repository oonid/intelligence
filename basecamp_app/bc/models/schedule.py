from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from bc.models import BcPeople, BcProject, BcRecurrenceSchedule


class BcSchedule(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/schedules.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Schedule ID
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
    include_due_assignments = models.BooleanField()
    entries_count = models.IntegerField()
    entries_url = models.URLField()

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'


class BcScheduleEntry(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/schedule_entries.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Schedule Entry ID
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
    # parent in ["Schedule"]
    parent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_object_id = models.PositiveIntegerField()
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    parent = GenericForeignKey("parent_content_type", "parent_object_id")
    bucket = models.ForeignKey(to=BcProject, on_delete=models.CASCADE)
    creator = models.ForeignKey(to=BcPeople, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    summary = models.CharField(max_length=100)
    all_day = models.BooleanField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    # null has no effect on ManyToManyField, set blank=True to make it optional
    participants = models.ManyToManyField(to=BcPeople, related_name='schedule_entry_participants')
    recurrence_schedule = models.ForeignKey(to=BcRecurrenceSchedule, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'
