import datetime
import os
import uuid
from mongocon.connection import task_user
from bson import ObjectId
from django.http import FileResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiParameter, extend_schema_serializer
from mongoengine import DoesNotExist
from rest_framework import permissions, status, renderers
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser, JSONParser
from rest_framework.response import Response

from company.models import Company
from mongocon.mongo_models import Task, TaskFieldModel, TaskFieldTypeModel, TaskUser
from .models import File
from .serializers import NoOpSerializer, TaskUserSerializer, TaskSerializer, FileSerializer, TaskAllSerializer

import json


# Create your views here.


class TaskUserListView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TaskUserSerializer
    parser_classes = (MultiPartParser, FileUploadParser)
    renderer_classes = (renderers.JSONRenderer,)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'task_id': {'type': 'string'},
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'fields': {'type': 'array', 'items':
                        {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string'},
                                'type': {'type': 'string'},
                                'content': {'type': 'string'},
                            }
                        }
                               },
                },
                'required': ['name', 'description', 'fields'],
            },
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            related_task = Task.objects(id=ObjectId(request.data.get('task_id')),
                                        assigned_to__contains=request.user.id).count()
            related_field = TaskUser.objects(task_id=request.data.get('task_id'), user_id=request.user.id).count()

            if related_field > 0:
                return Response("Task already exists", status=status.HTTP_400_BAD_REQUEST)
            if related_task == 0:
                return Response("Related task is not found or not assigned to this person.",
                                status=status.HTTP_400_BAD_REQUEST)
            data = request.data
            data["user_id"] = request.user.id
            data["created_by"] = request.user.id
            data["updated_by"] = request.user.id
            data["company_id"] = request.user.company_id
            data["status"] = "New"

            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                user_field = TaskUser(**serializer.validated_data)
                user_field.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


class TaskUserDetailView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TaskUserSerializer

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'task_id': {'type': 'string'},
                    'user_id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'fields': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'string'},
                                'name': {'type': 'string'},
                                'type': {'type': 'string'},
                                'content': {'type': 'string'},
                            }
                        }
                    },
                    'status': {'type': 'string'},
                    'company_id': {'type': 'integer'}
                },
                'required': ['task_id', 'user_id', 'name', 'description', 'fields', 'status', 'company_id']
            }
        },
        responses={
            200: OpenApiResponse(
                description="TaskUser updated successfully",
                examples={
                    'application/json': {
                        'task_id': 'string',
                        'user_id': 1,
                        'name': 'string',
                        'description': 'string',
                        'fields': [
                            {
                                'id': 'string',
                                'name': 'string',
                                'type': 'string',
                                'content': 'string'
                            }
                        ],
                        'status': 'string',
                        'company_id': 1
                    }
                }
            ),
            400: OpenApiResponse(
                description="Bad Request",
                examples={
                    'application/json': {
                        'error': 'Validation error message'
                    }
                }
            ),
            404: OpenApiResponse(
                description="Not Found",
                examples={
                    'application/json': {
                        'error': 'TaskUser not found'
                    }
                }
            ),
            500: OpenApiResponse(description="Internal Server Error"),
        },
        description="Update a TaskUser instance",
    )
    def put(self, request, task_id, *args, **kwargs):
        try:
            user_field = TaskUser.objects.get(task_id=task_id, user_id=request.user.id)
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user_field.update(**serializer.validated_data)
                user_field.reload()  # Refresh the document with updated data
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DoesNotExist:
            return Response({"error": "TaskUser not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, task_id, *args, **kwargs):
        task_id = str(task_id)
        related_task = Task.objects(id=task_id,
                                    assigned_to__contains=request.user.id).count()

        if related_task == 0:
            return Response("Related task is not found or not assigned to this person.",
                            status=status.HTTP_400_BAD_REQUEST)

        related_field = TaskUser.objects(task_id=task_id, user_id=request.user.id).first()

        if related_field is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(related_field)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskListView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'fields': {'type': 'array', 'items':
                        {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string'},
                                'type': {'type': 'string'},
                            }
                        }
                               },
                    'assigned_to': {'type': 'array', 'items': {'type': 'integer'}}
                },
                'required': ['name', 'description', 'fields', 'user_ids'],
            },
        },
        responses={
            200: OpenApiResponse(
                description="Task created successfully",
                examples={
                    'application/json': {
                        'task': {
                            'id': 'string',
                            'name': 'string',
                            'description': 'string',
                            'fields': [
                                {'type': 'string', 'name': 'string'}
                            ],
                        }
                    }
                }
            ),
            500: OpenApiResponse(description="Internal Server Error"),
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            data["created_by"] = request.user.id
            data["updated_by"] = request.user.id
            data["company_id"] = request.user.company_id
            data["status"] = "New"

            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                task = Task(**serializer.validated_data)
                task.save()
                task.reload()

                mongo_list = []

                mongo_data = {}

                mongo_data["name"] = task.name
                mongo_data["description"] = task.description
                mongo_data["task_id"] = str(task.id)

                mongo_data["created_by"] = request.user.id
                mongo_data["updated_by"] = request.user.id
                mongo_data["company_id"] = request.user.company_id
                mongo_data["status"] = "New"

                for assigned in task.assigned_to:
                    print(assigned)
                    fields = [
                        {
                            "id": i.id,
                            "name": i.name,
                            "type": i.type,
                            "content": "",
                            "represented_name": ""
                        }
                        for i in task.fields
                    ]
                    print(fields)
                    ids = [i.id for i in task.fields]
                    mongo_data["fields"] = fields

                    mongo_data["user_id"] = assigned
                    task_user_serializer = TaskUserSerializer(data=mongo_data)
                    if task_user_serializer.is_valid(raise_exception=True):
                        task = TaskUser(**task_user_serializer.validated_data)
                        for i in range(len(task.fields)):
                            task.fields[i].id = str(uuid.uuid4())
                        mongo_list.append(task.to_mongo())

                task_user.insert_many(mongo_list)

                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='skip', description='Number of items to skip', required=True, type=OpenApiTypes.INT),
            OpenApiParameter(name='limit', description='Maximum number of items to return', required=True,
                             type=OpenApiTypes.INT),
        ],
    )
    def get(self, request, *args, **kwargs):
        skip = 0
        limit = 0

        try:
            skip = int(request.query_params.get('skip'))
            limit = int(request.query_params.get('limit'))
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tasks = TaskUser.objects(user_id=request.user.id)[skip:limit + skip]
            count = TaskUser.objects(user_id=request.user.id).count()

            serialized_tasks = TaskUserSerializer(tasks, many=True)

            return Response({'data': serialized_tasks.data, 'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer

    def delete(self, request, _id, *args, **kwargs):
        if not request.user.is_manager:
            return Response("User is not authorized", status=status.HTTP_401_UNAUTHORIZED)

        try:
            task = Task.objects.get(id=_id)

            if task is None:
                return Response("Task not found", status=status.HTTP_404_NOT_FOUND)

            task.delete()

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response("Task deleted successfully", status=status.HTTP_200_OK)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'fields': {'type': 'array', 'items':
                        {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string'},
                                'type': {'type': 'string'},
                            }
                        }
                               },
                    'assigned_to': {'type': 'array', 'items': {'type': 'integer'}}
                },
                'required': ['name', 'description', 'fields', 'user_ids'],
            },
        },
        responses={
            200: OpenApiResponse(
                description="Task created successfully",
                examples={
                    'application/json': {
                        'task': {
                            'id': 'string',
                            'name': 'string',
                            'description': 'string',
                            'fields': [
                                {'type': 'string', 'name': 'string'}
                            ],
                        }
                    }
                }
            ),
            500: OpenApiResponse(description="Internal Server Error"),
        },
    )
    def put(self, request, _id, *args, **kwargs):
        if not request.user.is_manager:
            return Response("User is not authorized", status=status.HTTP_401_UNAUTHORIZED)

        try:
            task = Task.objects.get(id=_id)
            data = request.data
            data["updated_by"] = request.user.id
            data["updated_at"] = datetime.datetime.now()
            data["created_by"] = task.created_by
            data["created_at"] = task.created_at

            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                task.update(**serializer.validated_data)
                task.reload()  # Refresh the document with updated data
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DoesNotExist:
            return Response({"error": "TaskUser not found"}, status=status.HTTP_404_NOT_FOUND)


class AllTasksView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskAllSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='skip', description='Number of items to skip', required=True, type=OpenApiTypes.INT),
            OpenApiParameter(name='limit', description='Maximum number of items to return', required=True,
                             type=OpenApiTypes.INT),
        ],
    )
    def get(self, request, *args, **kwargs):
        skip = 0
        limit = 0

        if not request.user.is_manager:
            return Response("User is not a manager", status=status.HTTP_401_UNAUTHORIZED)

        try:
            skip = int(request.query_params.get('skip'))
            limit = int(request.query_params.get('limit'))
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tasks = Task.objects()[skip:limit + skip]
            count = Task.objects().count()

            serialized_tasks = self.serializer_class(tasks, many=True)

            return Response({'data': serialized_tasks.data, 'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def update_field_by_ids(content, task_id, user_id, field_id, represented_name=""):
    print(22)
    print(task_id, user_id, field_id)
    user_field = TaskUser.objects.get(task_id=task_id, user_id=user_id)

    print(33)
    if user_field is None:
        raise Exception("User Field not found")

    changed = False

    if represented_name == "":
        for i in range(len(user_field.fields)):
            if user_field.fields[i].id == field_id:
                user_field.fields[i].content = content
                changed = True
                break
    else:
        for i in range(len(user_field.fields)):
            print(user_field.fields[i].id, field_id)
            if user_field.fields[i].id == field_id:
                user_field.fields[i].content = content
                user_field.fields[i].represented_name = represented_name
                changed = True
                break

    if changed:
        user_field.status = "In Process"
        user_field.save()
    else:
        raise Exception("Field_id is not valid")



class FileView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FileSerializer

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, *args, **kwargs):
        try:
            task_id = str(request.query_params.get('task_id'))
            field_id = str(request.query_params.get('field_id'))

            if (task_id == "") or (field_id == ""):
                return Response({"error": "Field id or task id not found"}, status=status.HTTP_400_BAD_REQUEST)

            file = File.objects.filter(task_id=task_id, field_id=field_id, user_id=request.user.id,
                                       is_updated=False).first()

            if file is None:
                print(11)
                up_file = request.FILES['file']
                represent_name, file_extension = os.path.splitext(up_file.name)
                name = str(uuid.uuid4()) + file_extension
                destination_path = os.path.join('/Users/yurdasenalpyeni/Desktop/techarts/insanise/backend/media/', name)
                with open(destination_path, 'wb+') as destination:
                    for chunk in up_file.chunks():
                        destination.write(chunk)

                update_field_by_ids(content=name, task_id=task_id, user_id=request.user.id,
                                    field_id=field_id, represented_name=represent_name)

                print(44)
                """
                
                TO DO: task check
                
                """
                print(2)
                data = {
                    "represent_name": represent_name + file_extension,
                    "name": name,
                    "suffix": file_extension,
                    "company_id": request.user.company_id,
                    "created_by": request.user,
                    "updated_by": request.user,
                    "user": request.user,
                    "task_id": task_id,
                    "field_id": field_id,
                }
                print(3)
                file = File.objects.create(**data)
                print(4)
                return Response({"name": name, "represent_name": represent_name + file_extension},
                                status=status.HTTP_201_CREATED)
            else:
                print(1)
                up_file = request.FILES['file']
                represent_name, file_extension = os.path.splitext(up_file.name)
                name = str(uuid.uuid4()) + file_extension
                destination_path = os.path.join('/Users/yurdasenalpyeni/Desktop/techarts/insanise/backend/media/', name)
                with open(destination_path, 'wb+') as destination:
                    for chunk in up_file.chunks():
                        destination.write(chunk)
                print(2)
                update_field_by_ids(content=name, task_id=task_id, user_id=request.user.id,
                                    field_id=field_id, represented_name=represent_name)

                """
                TO DO: task check

                """
                print(3)
                file.is_updated = True
                file.updated_by_id = request.user.id
                file.save()
                print(4)
                data = {
                    "represent_name": represent_name + file_extension,
                    "name": name,
                    "suffix": file_extension,
                    "company_id": request.user.company_id,
                    "created_by": request.user,
                    "updated_by": request.user,
                    "user": request.user,
                    "task_id": task_id,
                    "field_id": field_id,
                }

                file = File.objects.create(**data)
                print(5)
                return Response({"name": name, "represent_name": represent_name + file_extension},
                                status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        task_id = str(request.query_params.get('task_id'))
        field_id = str(request.query_params.get('field_id'))
        user_id = request.user.id

        if (not task_id) or (not field_id):
            return Response({"error": "Field id or task id not found"}, status=status.HTTP_400_BAD_REQUEST)

        """
        TO DO: task check

        """

        file = File.objects.filter(task_id=task_id, field_id=field_id, user_id=request.user.id,
                                   is_updated=False).first()

        if file is None:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(open("/Users/yurdasenalpyeni/Desktop/techarts/insanise/backend/media/" + file.name, 'rb'))

    def delete(self, request, *args, **kwargs):
        task_id = str(request.query_params.get('task_id'))
        field_id = str(request.query_params.get('field_id'))

        user_id = request.user.id

        if (not task_id) or (not field_id):
            return Response({"error": "Field id or task id not found"}, status=status.HTTP_400_BAD_REQUEST)

        file = File.objects.filter(task_id=task_id, field_id=field_id, user_id=request.user.id,
                                   is_updated=False).first()

        if file is None:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        file.is_updated = True
        file.updated_by_id = request.user.id
        file.save()

        return Response({"message": "File deleted"}, status=status.HTTP_200_OK)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'content': {'type': 'string'},
                    'task_id': {'type': 'string'},
                    'field_id': {'type': 'string'}
                },
                'required': ['content', 'task_id', 'field_id']
            }
        },
        responses={200: OpenApiTypes.OBJECT}  # Modify response type based on your needs
    )
    def put(self, request, *args, **kwargs):
        try:
            task_id = request.data.get('task_id')
            field_id = request.data.get('field_id')
            content = request.data.get('content')
            user_id = request.user.id

            print(2)
            if (not task_id) or (not field_id):
                return Response({"error": "Field id or task id not found"}, status=status.HTTP_400_BAD_REQUEST)

            if not content:
                return Response({"error": "Content cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

            print(4)

            update_field_by_ids(task_id=task_id, field_id=field_id, user_id=request.user.id, content=content)

            return Response({"message": "Field updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
