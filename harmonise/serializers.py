from rest_framework import serializers

from company.models import Company
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
    name = serializers.CharField(required=True)
    type = serializers.CharField(required=True)


class TaskSerializer(serializers.Serializer):
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


class TaskFieldModelSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    name = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    content = serializers.CharField(required=True)


class UserFieldSerializer(serializers.Serializer):
    task_id = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=200, required=True)
    description = serializers.CharField(max_length=200, required=True)
    fields = TaskFieldModelSerializer(many=True)
    status = serializers.CharField(required=True)
    company_id = serializers.IntegerField(required=True)
    updated_by = serializers.IntegerField(required=True)
    created_by = serializers.IntegerField(required=True)


class FileSerializer(serializers.Serializer):
    class Meta:
        model = File
        fields = ['name', 'suffix', 'company', 'created_at', 'updated_at', 'created_by', 'updated_by', 'user', 'file']

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