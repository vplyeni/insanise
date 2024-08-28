from datetime import datetime
from rest_framework import serializers
from harmonise.models import File


class NoOpSerializer(serializers.Serializer):
    def to_representation(self, instance):
        # This method is used to convert the object instance to a dictionary of primitive datatypes.
        return instance

    def to_internal_value(self, data):
        # This method is used to convert the input data into a validated dictionary of datatypes.
        return data

    def create(self, validated_data):
        # If you're using this with model serializers, you can override the create method.
        return validated_data

    def update(self, instance, validated_data):
        # Similarly, override update if necessary.
        return validated_data


class TaskFieldTypeModelSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True, required=False)
    name = serializers.CharField(required=True)
    type = serializers.CharField(required=True)


class TaskSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)

    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)

    created_by = serializers.IntegerField(required=True)
    updated_by = serializers.IntegerField(required=True)

    status = serializers.CharField(required=True)
    company_id = serializers.IntegerField(required=True)
    assigned_to = serializers.ListField(child=serializers.IntegerField())
    fields = TaskFieldTypeModelSerializer(many=True)

    task_period = serializers.IntegerField(required=True)


class ManagerTaskSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)

    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)

    created_by = serializers.IntegerField(required=True)
    updated_by = serializers.IntegerField(required=True)

    status = serializers.CharField(required=True)
    company_id = serializers.IntegerField(required=True)
    assigned_to = serializers.ListField(child=serializers.IntegerField())
    fields = TaskFieldTypeModelSerializer(many=True)

    task_period = serializers.IntegerField(required=False, default=0)


class TaskFieldModelSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, read_only=True)
    name = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    content = serializers.CharField(required=False, allow_blank=True)
    represented_name = serializers.CharField(required=False, allow_blank=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)


class TaskUserSerializer(serializers.Serializer):
    task_id = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)

    name = serializers.CharField(max_length=200, required=True)
    description = serializers.CharField(max_length=1000, required=True)
    fields = TaskFieldModelSerializer(many=True)

    status = serializers.CharField(required=True)

    company_id = serializers.IntegerField(required=True)
    updated_by = serializers.IntegerField(required=True)
    created_by = serializers.IntegerField(required=True)

    due_date = serializers.DateTimeField(required=True, format='%d-%m-%Y')


class FileSerializer(serializers.Serializer):
    class Meta:
        model = File
        fields = ["represent_name", 'name', 'suffix', 'company', 'created_at',
                  'updated_at', 'created_by', 'updated_by', 'user', 'file']

    def create(self, validated_data):
        print(validated_data)
        # Create and return a new instance of YourModel
        return File.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.updated_by = validated_data.get('updated_by', instance.updated_by)
        instance.user = validated_data.get('user', instance.user)
        # Update other fields as necessary
        instance.save()
        return instance

class AssignAndWithdrawSerializer(serializers.Serializer):
    task_id = serializers.CharField(required=True)
    assigned_period = serializers.IntegerField(required=False, allow_null=True)
    assigned_to = serializers.ListField(child=serializers.IntegerField())
