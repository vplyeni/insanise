from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task, TaskEmployee, Field, FieldEmployee
from .serializers import TaskSerializer, TaskEmployeeSerializer, FieldSerializer, FieldEmployeeSerializer
from rest_framework import viewsets

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer



