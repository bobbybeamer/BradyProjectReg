from rest_framework import serializers
from .models import Deal, DealAudit


class DealAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealAudit
        fields = ['id', 'deal', 'changed_by', 'old_status', 'new_status', 'timestamp', 'note']


class DealSerializer(serializers.ModelSerializer):
    audit_trail = DealAuditSerializer(read_only=True, many=True)

    class Meta:
        model = Deal
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'expiry_date')
        extra_kwargs = {
            'partner': {'read_only': True},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.role == 'PARTNER':
            validated_data['partner'] = user.partner_organisation
        return super().create(validated_data)

    def validate(self, data):
        user = self.context['request'].user
        if user.is_authenticated and user.role == 'PARTNER':
            # Partner cannot create/edit deals for other organisations
            partner = getattr(user, 'partner_organisation', None)
            if not partner:
                raise serializers.ValidationError('Partner user must belong to an organisation')
            if self.instance is None:
                data['partner'] = partner
            else:
                # ensure partner didn't change partner field
                if 'partner' in data and data['partner'] != self.instance.partner:
                    raise serializers.ValidationError('Cannot change partner organisation')
            # check status editing rules
            if self.instance and self.instance.status not in ('DRAFT', 'SUBMITTED'):
                # allow read only
                raise serializers.ValidationError('Cannot edit deal unless status is Draft or Submitted')
        return data

    def update(self, instance, validated_data):
        # pass the user to signals for audit logging
        request = self.context.get('request')
        if request:
            instance._changed_by = request.user
        return super().update(instance, validated_data)

    def create(self, validated_data):
        request = self.context.get('request')
        return super().create(validated_data)
