from rest_framework import serializers
from .models import Task, TaskEmployee, Field, FieldEmployee


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'  # Or specify individual fields


class TaskEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskEmployee
        fields = '__all__'


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = '__all__'


class FieldEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldEmployee
        fields = '__all__'
