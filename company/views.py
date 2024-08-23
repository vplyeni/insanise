# myapp/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.views import View
from django.http import HttpResponse
from .models import Company, TargetGroup, Team, Employee
from .serializers import CompanySerializer, TargetGroupSerializer, TeamSerializer, EmployeeSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class TargetGroupViewSet(viewsets.ModelViewSet):
    queryset = TargetGroup.objects.all()
    serializer_class = TargetGroupSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
