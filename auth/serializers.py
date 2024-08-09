from rest_framework import serializers
from company.models import Employee

class EmployeeDTO(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email', 'position', 'department', 'date_of_birth', 'company', 'target_group', 'team']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"