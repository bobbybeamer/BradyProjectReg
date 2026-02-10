from rest_framework import serializers
from .models import User, PartnerOrganisation


class PartnerOrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerOrganisation
        fields = ['id', 'name', 'status', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    partner_organisation = PartnerOrganisationSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'partner_organisation']
        read_only_fields = ['role']
