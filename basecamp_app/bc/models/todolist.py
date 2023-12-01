from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from bc.models import BcTodoBase


class BcTodolist(BcTodoBase):
    """
    the model represent todolist and todolist_group.
    in terms of "parent", the bc api using same terms, no todolist_group as parent.
    add (internal) new field is_todolist_group to differ todolist and todolist_group

    https://github.com/basecamp/bc3-api/blob/master/sections/todolists.md
    https://github.com/basecamp/bc3-api/blob/master/sections/todolist_groups.md
    """
    completed_ratio = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    # completed_ratio and name not available at Todo
    subscription_url = models.URLField()
    comments_count = models.IntegerField()
    comments_url = models.URLField()
    # parent in ["Todoset", "Todolist"]
    parent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_object_id = models.PositiveIntegerField()
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    parent = GenericForeignKey("parent_content_type", "parent_object_id")
    description = models.CharField(max_length=100)
    todos_url = models.URLField()
    app_todos_url = models.URLField()
    # field of BcTodolist, the difference from BcTodolistGroup
    groups_url = models.URLField(null=True, blank=True)
    # field of BcTodolistGroup, the difference from BcTodolist
    group_position_url = models.URLField(null=True, blank=True)
    # internal field (not available at bc api): True means todolist_group, False means todolist
    is_todolist_group = models.BooleanField()

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'
