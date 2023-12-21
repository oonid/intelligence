from rest_framework import serializers

from bc.models import BcCompany


class BcCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = BcCompany
        fields = ['id', 'name']

    # not implement create, as it will use the create method from parent (ModelSerializer)
    # if implement create at child, calling method create will only call method at child (no parent method called)
