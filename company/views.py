# myapp/views.py
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Company, TargetGroup, Team, Employee
from .permissions import IsManager, IsSuperUser
from .serializers import CompanySerializer, TargetGroupSerializer, TeamSerializer, EmployeeSerializer, \
    EmployeeSearchSerializer


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
        ],
    )
    def list(self, request):
        skip = 0
        limit = 5

        try:
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

    @extend_schema(
        parameters=[
            OpenApiParameter(name='skip', description='Number of items to skip', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='limit', description='Maximum number of items to return', required=False,
                             type=OpenApiTypes.INT),
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {'search': {'type': 'string'},
                               'selected_employees': {'type': 'array', 'items': {'type': 'integer'}
                                                      },
                               'required': ['search', 'selected_employees'],
                               },
            }
        }

    )
    @action(methods=["POST"], detail=False)
    def search(self, request, *args, **kwargs):
        search_text = ""
        selected_employees = []

        search_serializer = EmployeeSearchSerializer(data=request.data)
        search_serializer.is_valid(raise_exception=True)

        if search_serializer.validated_data.get('search') is not None:
            search_text = search_serializer.validated_data.get('search')

        if search_serializer.validated_data.get('selected_employees') is not None:
            selected_employees = search_serializer.validated_data.get('selected_employees')

        skip = 0
        limit = 5

        try:
            skip = int(request.query_params.get('skip'))
            limit = int(request.query_params.get('limit'))
        except Exception as e:
            print(e)

        count = Employee.objects.exclude(id__in=selected_employees).filter(full_name__icontains=search_text).count()
        employees = Employee.objects.exclude(id__in=selected_employees).filter(
            full_name__icontains=search_text).order_by('id')
        employee_serializer = self.serializer_class(employees, many=True)

        return Response({'data': employee_serializer.data, 'count': count}, status=status.HTTP_200_OK)