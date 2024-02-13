from django.db import models


class BcProjectTool(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/projects.md#get-a-project
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Project Tool ID
    title = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    enabled = models.BooleanField()
    position = models.IntegerField(null=True)
    url = models.URLField()
    app_url = models.URLField()

    def __str__(self):
        return f'{self.id} {self.name} {self.title} ({self.enabled})'


class BcProject(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/projects.md
    excluded field(s): bookmarked, last_needle_color, last_needle_position, previous_needle_position
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Project ID
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    purpose = models.CharField(max_length=30)
    clients_enabled = models.BooleanField()
    bookmark_url = models.URLField()
    url = models.URLField()
    app_url = models.URLField()
    dock = models.ManyToManyField(to=BcProjectTool)

    def __str__(self):
        return f'{self.id} {self.purpose} {self.name}'
