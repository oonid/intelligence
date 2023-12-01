from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from bc.models import BcTodoBase, BcPeople, BcRecurrenceSchedule


class BcTodoCompletion(models.Model):
    """
    field completion on todo
    """
    created_at = models.DateTimeField(db_index=True)
    creator = models.ForeignKey(to=BcPeople, on_delete=models.CASCADE)


class BcTodo(BcTodoBase):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/todos.md
    """
    subscription_url = models.URLField()
    comments_count = models.IntegerField()
    comments_url = models.URLField()
    # parent in ["Todoset", "Todolist"]
    parent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_object_id = models.PositiveIntegerField()
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    parent = GenericForeignKey("parent_content_type", "parent_object_id")
    description = models.CharField(max_length=100)
    completion = models.ForeignKey(to=BcTodoCompletion, on_delete=models.CASCADE, null=True, blank=True)
    content = models.CharField(max_length=100)
    starts_on = models.DateField(null=True)
    due_on = models.DateField(null=True)
    repetition_schedule = models.ForeignKey(to=BcRecurrenceSchedule, on_delete=models.CASCADE, null=True, blank=True)
    # null has no effect on ManyToManyField, set blank=True to make it optional
    assignees = models.ManyToManyField(to=BcPeople, blank=True,
                                       related_name='todo_assignees')
    # null has no effect on ManyToManyField, set blank=True to make it optional
    completion_subscribers = models.ManyToManyField(to=BcPeople, blank=True,
                                                    related_name='todo_completion_subscribers')
    completion_url = models.URLField()

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'
