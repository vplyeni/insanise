from django.contrib.auth.hashers import make_password
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Company, TargetGroup, Team, Employee


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'  # Or specify individual fields


class TargetGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetGroup
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

    def to_internal_value(self, data):
        # Hash the password before saving
        if 'password' in data:
            data['password'] = make_password(data['password'])
        return super().to_internal_value(data)

    def to_representation(self, instance):
        # Get the standard representation from the parent class
        ret = super().to_representation(instance)

        # Remove the password field from the output
        ret.pop('password', None)
        return ret


class EmployeeSearchSerializer(serializers.Serializer):
    search = serializers.CharField()
    selected_employees = serializers.ListField(child=serializers.IntegerField())
