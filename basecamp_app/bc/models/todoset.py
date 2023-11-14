from django.db import models
from bc.models import BcTodoBase


class BcTodoset(BcTodoBase):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/todosets.md
    """
    completed_ratio = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    # completed_ratio and name not available at Todo
    todolists_count = models.IntegerField()
    todolists_url = models.URLField()
    app_todoslists_url = models.URLField()

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'
