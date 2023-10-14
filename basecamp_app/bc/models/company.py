from django.db import models


class BcCompany(models.Model):
    id = models.BigIntegerField(primary_key=True)  # Basecamp Company ID
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.id} {self.name}'
