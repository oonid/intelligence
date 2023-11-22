from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from bc.models import BcPeople, BcProject


class BcRecurrenceSchedule(models.Model):
    """
    used by:
    * Question Schedule: https://github.com/basecamp/bc3-api/blob/master/sections/questions.md
    * Recurrence Schedule Entry: https://github.com/basecamp/bc3-api/blob/master/sections/schedule_entries.md
    """
    frequency = models.CharField(max_length=30)
    # PostgreSQL has ArrayField: https://docs.djangoproject.com/en/4.2/ref/contrib/postgres/fields/#arrayfield
    # to support SQLite use JSONField: https://docs.djangoproject.com/en/4.2/ref/models/fields/#jsonfield
    days = models.JSONField(null=True, blank=True)  # days is a list of integers
    hour = models.IntegerField()
    minute = models.IntegerField()
    week_instance = models.IntegerField(null=True, blank=True)
    week_interval = models.IntegerField(null=True, blank=True)  # todo: example of week_interval
    month_interval = models.IntegerField(null=True, blank=True)  # todo: example of month_interval
    start_date = models.DateField()
    duration = models.IntegerField(null=True, blank=True)  # annual -> 32400
    end_date = models.DateField(null=True, blank=True)


class BcQuestionnaire(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/questionnaires.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Questionnaire ID
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
    name = models.CharField(max_length=100)
    questions_count = models.IntegerField()
    questions_url = models.URLField()

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'


class BcQuestion(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/questions.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Question ID
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
    # parent in ["Questionnaire"]
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    parent = GenericForeignKey("content_type", "object_id")
    bucket = models.ForeignKey(to=BcProject, on_delete=models.CASCADE)
    creator = models.ForeignKey(to=BcPeople, on_delete=models.CASCADE)
    paused = models.BooleanField()
    # TODO: prefer using BcRecurrenceSchedule or JSONField?
    schedule = models.ForeignKey(to=BcRecurrenceSchedule, on_delete=models.CASCADE)
    answers_count = models.IntegerField()
    answers_url = models.URLField()

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'


class BcQuestionAnswer(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/question_answers.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Question Answer ID
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
    # parent in ["Question"]
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    parent = GenericForeignKey("content_type", "object_id")
    bucket = models.ForeignKey(to=BcProject, on_delete=models.CASCADE)
    creator = models.ForeignKey(to=BcPeople, on_delete=models.CASCADE)
    content = models.TextField()
    group_on = models.DateField(null=True)

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'
