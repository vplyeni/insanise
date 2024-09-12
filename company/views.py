# myapp/views.py
import secrets
import string

from mailer import mailer

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

    # Custom create method
    def create(self, request, *args, **kwargs):
        request.data["company"] = request.user.company_id
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        skip = 0
        limit = 5

        try:
            if request.query_params.get('skip') is not None and request.query_params.get('limit') is not None:
                skip = int(request.query_params.get('skip'))
                limit = int(request.query_params.get('limit'))
        except Exception as e:
            print(e)

        target_groups = self.queryset.all().filter(company_id=request.user.company_id).order_by('id')[skip:skip + limit]
        count = self.queryset.all().count()

        target_groups = self.serializer_class(target_groups, many=True)

        return Response({"data": target_groups.data, "count": count}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        request.data["company"] = request.user.company_id
        instance = self.get_object()

        if instance.company_id != request.user.company_id:
            return Response({"error": "You cannot update the company yourself!"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def create(self, request, *args, **kwargs):
        request.data["company"] = request.user.company_id
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        skip = 0
        limit = 5

        try:
            if request.query_params.get('skip') is not None and request.query_params.get('limit') is not None:
                skip = int(request.query_params.get('skip'))
                limit = int(request.query_params.get('limit'))
        except Exception as e:
            print(e)

        target_groups = self.queryset.all().filter(company_id=request.user.company_id).order_by('id')[skip:skip + limit]
        count = self.queryset.all().count()

        target_groups = self.serializer_class(target_groups, many=True)

        return Response({"data": target_groups.data, "count": count}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        request.data["company"] = request.user.company_id
        instance = self.get_object()

        if instance.company_id != request.user.company_id:
            return Response({"error": "You cannot update the company yourself!"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        request.data["company"] = request.user.company_id
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


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

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            if not request.user.is_superuser:
                serializer.data["company_id"] = request.user.company_id
                serializer.data["is_superuser"] = False

            Employee.objects.create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=["POST"], detail=False)
    def create_employee(self, request, *args, **kwargs):
        # Generate a random password
        password_length = 12
        password_characters = string.ascii_letters + string.digits + string.punctuation
        random_password = ''.join(secrets.choice(password_characters) for _ in range(password_length))

        # Add the random password to the request data
        data = request.data.copy()
        data['password'] = random_password

        # Create the employee
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Return the created employee's data (excluding the password if needed)
        response_data = serializer.data
        response_data.pop('password', None)  # Remove password from response

        print(random_password)

        address = data['email']
        header = "Your Insanise Account Has Been Created"
        content = ("Dear " + data["first_name"] + ",\n \n"
                   + "Your Insanise Account Has Been Created. \n \n"
                   + "Your Password: " + random_password)

        mailer.send(address, headerss, content)

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    """"
    def update(self, request, pk=None, *args, **kwargs):
        try:
            employee = self.get_object()

            request.data["password"] = employee.password

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=False)
            self.check_object_permissions(request, serializer.data)

            Employee.objects.update(**serializer.data)

            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)"""

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            employee = self.get_object()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=["POST"], detail=False)
    def get_employee_by_id_list(self, request, *args, **kwargs):
        list = []

        if request.data.get("employees"):
            list = request.data.get("employees")
        else:
            return Response({'error': 'Employee list field is required'}, status=status.HTTP_400_BAD_REQUEST)

        employees = Employee.objects.filter(id__in=list)

        serializer = self.serializer_class(employees, many=True)

        serializer.is_valid(raise_exception=True)

        return Response({'employees': serializer.validated_data}, status=status.HTTP_200_OK)
