from rest_framework import serializers

from bc.models import BcPeople, BcCompany
from bc.serializers import BcCompanySerializer


class BcPeopleSerializer(serializers.ModelSerializer):
    company = BcCompanySerializer()

    def to_internal_value(self, data):
        """https://www.django-rest-framework.org/api-guide/serializers/#to_internal_valueself-data
        override this method because overwrite method create, always get exists of creator and bucket
        this method called before create, and this override make the creator and bucket can use existing
        this method called before is_valid(), so no validated_data
        """
        # create or get company instance from request data, remove (pop) the company field from data
        company_data = data.pop('company')
        try:
            company = BcCompany.objects.get(id=company_data["id"])
        except BcCompany.DoesNotExist:
            # create new company if the id does not exist
            company = BcCompany.objects.create(**company_data)
        # assign the company to serializer
        self.company = company

        # exclude 'can_ping' field from data, as we currently did not use the field
        data.pop('can_ping')

        if 'out_of_office' in data:  # exclude 'out_of_office' field from data, as we currently did not use the field
            data.pop('out_of_office')

        return data  # return data without the company field

    class Meta:
        model = BcPeople
        fields = ['id', 'attachable_sgid', 'name', 'email_address', 'personable_type', 'title', 'bio', 'location',
                  'created_at', 'updated_at', 'admin', 'owner', 'client', 'employee', 'time_zone', 'avatar_url',
                  'can_manage_projects', 'can_manage_people', 'company']

    def create(self, validated_data):
        # by using to_internal_value above, the validation process is disabled, validated_data can contain existing data
        # instead of create new data, load the data from model if it has same id or email address
        people = None
        if 'id' in validated_data:
            id_data = validated_data.get('id')
            try:
                people = BcPeople.objects.get(id=id_data)
            except BcPeople.DoesNotExist:
                people = None
        if people:
            return people  # found by id

        if 'email_address' in validated_data:
            email_address_data = validated_data.get('email_address')
            people = BcPeople.objects.filter(email_address=email_address_data).first()
        if people:
            return people  # found by email_address

        # still not found, create the data

        if self.company:  # previously assigned from to_internal_value()
            people = BcPeople.objects.create(company=self.company, **validated_data)
        else:  # on any other condition assign fully from validated_data
            people = BcPeople.objects.create(**validated_data)
        return people
