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