import datetime
import uuid

from bson import ObjectId
from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiParameter
from mongoengine import DoesNotExist
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from mongocon.mongo_models import Task, TaskFieldModel, TaskFieldTypeModel, UserField
from .serializers import NoOpSerializer, UserFieldSerializer

import json


# Create your views here.

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
class UserFieldListView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NoOpSerializer

    def post(self, request, *args, **kwargs):
        related_task = Task.objects(id=ObjectId(request.data.get('task_id')),
                                    assigned_to__contains=request.user.id).count()
        related_field = UserField.objects(task_id=request.data.get('task_id'), user_id=request.user.id).count()

        if related_field > 0:
            return Response("Task already exists", status=status.HTTP_400_BAD_REQUEST)
        if related_task == 0:
            return Response("Related task is not found or not assigned to this person.",
                            status=status.HTTP_400_BAD_REQUEST)
        print(1)

        fields = [
            {
                "id": str(uuid.uuid4()),
                "name": i.get("name"),
                "type": i.get("type"),
                "content": i.get("content"),
            }

            for i in request.data.get('fields')
        ]

        print(2)
        user_field = UserField(
            task_id=request.data.get('task_id'),
            user_id=request.user.id,

            name=request.data.get('name'),
            description=request.data.get('description'),

            fields=fields,

            created_by=request.user.id,
            updated_by=request.user.id,

            status="not_complete",
            company_id=request.user.company_id,
        )
        print(3)
        user_field.save()
        print(4)
        return Response(json.loads(user_field.to_json()), status=status.HTTP_201_CREATED)


class UserFieldDetailView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserFieldSerializer

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
                description="UserField updated successfully",
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
                        'error': 'UserField not found'
                    }
                }
            ),
            500: OpenApiResponse(description="Internal Server Error"),
        },
        description="Update a UserField instance",
    )
    def put(self, request, task_id, *args, **kwargs):
        print(3)
        try:
            user_field = UserField.objects.get(task_id=task_id,user_id=request.user.id)
            serializer = UserFieldSerializer(data=request.data)
            if serializer.is_valid():
                user_field.update(**serializer.validated_data)
                user_field.reload()  # Refresh the document with updated data
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DoesNotExist:
            return Response({"error": "UserField not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, task_id, *args, **kwargs):
        print(2)
        task_id = str(task_id)
        related_task = Task.objects(id=task_id,
                                    assigned_to__contains=request.user.id).count()

        if related_task == 0:
            return Response("Related task is not found or not assigned to this person.",
                            status=status.HTTP_400_BAD_REQUEST)

        related_field = UserField.objects(task_id=task_id, user_id=request.user.id).first()

        if related_field is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(json.loads(related_field.to_json()), status=status.HTTP_200_OK)



class TaskListView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NoOpSerializer

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
            fields = [TaskFieldTypeModel(
                name=i.get("name"),
                type=i.get("type"),
            ) for i in request.data.get('fields')]

            assigned_to = [int(i) for i in request.data.get('assigned_to')]

            task = Task(name=request.data.get('name'),
                        description=request.data.get('description'),

                        fields=fields,
                        assigned_to=assigned_to,

                        created_by=request.user.id,
                        updated_by=request.user.id,

                        company_id=request.user.company_id,
                        status="new"
                        )
            task.save()

            return Response(json.loads(task.to_json())
                            , status=status.HTTP_201_CREATED)
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
            print(skip, limit)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tasks = Task.objects(assigned_to__contains=request.user.id)[skip:limit + skip]
            count = Task.objects(assigned_to__contains=request.user.id).count()
            print(tasks)
            return Response({'data': json.loads(tasks.to_json()), 'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NoOpSerializer

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

    def put(self, request, _id, *args, **kwargs):
        if not request.user.is_manager:
            return Response("User is not authorized", status=status.HTTP_401_UNAUTHORIZED)

        return Response("TODO", status=status.HTTP_405_METHOD_NOT_ALLOWED)
