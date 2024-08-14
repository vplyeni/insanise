from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    _id = serializers.IntegerField()