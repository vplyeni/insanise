from django.shortcuts import render
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from mongocon.mongo_models import Task
from .serializers import NoOpSerializer

# Create your views here.


class TaskView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NoOpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.validated_data['task']


