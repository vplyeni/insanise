# myapp/views.py
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from .models import Company, TargetGroup, Team, Employee
from .permissions import IsManager, IsSuperUser
from .serializers import CompanySerializer, TargetGroupSerializer, TeamSerializer, EmployeeSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]


class TargetGroupViewSet(viewsets.ModelViewSet):
    queryset = TargetGroup.objects.all()
    serializer_class = TargetGroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='skip', description='Number of items to skip', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='limit', description='Maximum number of items to return', required=False,
                             type=OpenApiTypes.INT),
            OpenApiParameter(name='search', description='Search', required=False,
                             type=OpenApiTypes.STR),
        ],
    )
    def list(self, request):
        skip = 0
        limit = 5
        search = ""

        try:
            skip = int(request.query_params.get('search'))
            skip = int(request.query_params.get('skip'))
            limit = int(request.query_params.get('limit'))
        except Exception as e:
            print(e)

        try:
            employees = self.queryset.order_by('id')[skip:limit + skip]
            count = self.queryset.count()

            serialized_employees = self.serializer_class(employees, many=True)

            return Response({'data': serialized_employees.data, 'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
