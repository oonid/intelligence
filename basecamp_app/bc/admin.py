from django.contrib import admin
from .models import BcCompany, BcPeople

# Register your models here.

admin.site.register(BcCompany)
admin.site.register(BcPeople)
