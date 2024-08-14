from rest_framework import serializers


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


class TaskSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()

    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    created_by = serializers.IntegerField()
    updated_by = serializers.IntegerField()

    status = serializers.CharField()

    company_id = serializers.IntegerField()

    assigned_to = serializers.ListField(child=serializers.IntegerField())


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
