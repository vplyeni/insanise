from rest_framework import serializers

from leave.models import Leave


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'

    def to_internal_value(self, data):
        # Hash the password before saving
        return super().to_internal_value(data)

    def to_representation(self, instance):
        # Get the standard representation from the parent class
        ret = super().to_representation(instance)
        return ret
