from rest_framework import serializers

from bc.models import BcCompany


class BcCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = BcCompany
        fields = ['id', 'name']

    def create(self, validated_data):
        print(f'BcCompanySerializer.create: {validated_data}')
