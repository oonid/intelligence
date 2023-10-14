from django.db import models
from .company import BcCompany  # not using "from bc.models" which triggered circular import


class BcPeople(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/people.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp User ID
    attachable_sgid = models.TextField(null=True, blank=True)  # attachment sgid (eg: mention user)
    name = models.CharField(max_length=100)
    email_address = models.EmailField(unique=True)
    personable_type = models.CharField(max_length=30)
    title = models.CharField(max_length=100)
    bio = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField()
    admin = models.BooleanField()
    owner = models.BooleanField()
    client = models.BooleanField()
    employee = models.BooleanField()
    time_zone = models.CharField(max_length=30)
    avatar_url = models.URLField(null=True, blank=True)
    can_manage_projects = models.BooleanField()
    can_manage_people = models.BooleanField()
    company = models.ForeignKey(to=BcCompany, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id} {self.name} {self.email_address}'
