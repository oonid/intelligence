from django.db import models
from bc.models import BcProject, BcPeople


class BcTodoBase(models.Model):
    """
    base class for:
    * todo: https://github.com/basecamp/bc3-api/blob/master/sections/todos.md
    * todoset: https://github.com/basecamp/bc3-api/blob/master/sections/todosets.md
    * todolist: https://github.com/basecamp/bc3-api/blob/master/sections/todolists.md
    * todolist_group: https://github.com/basecamp/bc3-api/blob/master/sections/todolist_groups.md

    can not use "abstract", because ForeignKey can not refer to abstract model.
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Todoset ID
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
    completed = models.BooleanField()

    class Meta:
        abstract = True
