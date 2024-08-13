from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiParameter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .mongo_crud import (create_task, get_tasks_by_user_id, update_task, delete_task,
                         create_or_update_field, get_fields_by_user_id_task_id,
                         get_fields_by_user_id, delete_field, update_field)
from harmonise.serializers import NoOpSerializer
from .mongo_models import TaskFieldModel, FieldCreateModel
import json


def mongo_to_task_field_model(mongo):
    if mongo.get('id') is not None:
        field = TaskFieldModel(_id=mongo.get('id'), name=mongo.get('name'), _type=mongo.get('type'),
                               content=mongo.get('content'))
        return field
    else:
        field = TaskFieldModel(name=mongo.get('name'), _type=mongo.get('type'),
                               content=mongo.get('content'))
        return field


def mongo_to_field_model(mongo):
    task_fields = [TaskFieldModel(**json.loads(i)) for i in mongo.get('fields')]
    print(task_fields)
    """field = FieldCreateModel(task_id=mongo.get('task_id'), user_id=mongo.get('user_id'), created_at=mongo.get('created_at'), updated_at=mongo.get('updated_at'), fields )"""


class TaskListView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NoOpSerializer

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Task get successfully",
                examples={
                    'application/json': {
                        'tasks': [
                            {'task_id': '1', 'task_name': 'Task 1'},
                            {'task_id': '2', 'task_name': 'Task 2'}
                        ]
                    }
                }
            ),
            400: OpenApiResponse(
                description="Bad Request",
                examples={
                    'application/json': {
                        'error': 'user_id is required'
                    }
                }
            ),
            500: OpenApiResponse(
                description="Internal Server Error",
                examples={
                    'application/json': {
                        'error': 'An unexpected error occurred'
                    }
                }
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        user_id = request.user.id

        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_id = str(user_id)
            tasks = get_tasks_by_user_id(user_id)

            print(tasks)
            return Response({'tasks': tasks}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'fields': {'type': 'array', 'items': {'type': 'object'}},
                    'user_ids': {'type': 'array', 'items': {'type': 'string'}}
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
    def post(self, request, **kwargs):
        try:
            if not request.user.is_manager:
                return Response("User must be manager in order to assign Tasks", status=status.HTTP_403_FORBIDDEN)
            task = create_task(name=request.data.get('name'), description=request.data.get('description'),
                               fields=request.data.get('fields'), user_ids=request.data.get('user_ids'),
                               creator_user=request.user)
            return Response(task.to_dict(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NoOpSerializer

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'fields': {'type': 'array', 'items': {'type': 'object'}},
                    'user_ids': {'type': 'array', 'items': {'type': 'string'}}
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
        try:
            task = update_task(updater_user=request.user, _id=_id, name=request.data.get('name'),
                               description=request.data.get('description'),
                               fields=request.data.get('fields'), user_ids=request.data.get('user_ids'))
            return Response(task.to_dict(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, _id, *args, **kwargs):
        try:
            task = delete_task(user=request.user, _id=_id)
            return Response({"deleted": task.to_dict()}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FieldView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NoOpSerializer

    def get(self, request, *args, **kwargs):
        found_fields = get_fields_by_user_id(request.user.id)

        return Response([found_field.to_dict() for found_field in found_fields], status=status.HTTP_200_OK)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'task_id': {'type': 'string'},
                    'created_at': {'type': 'string'},
                    'updated_at': {'type': 'string'},
                    'fields': {'type': 'array', 'items': {'type': 'object',
                                                          'properties': {
                                                              'type': {'type': 'string'},
                                                              'name': {'type': 'string'},
                                                              'content': {'type': 'string'},
                                                          }
                                                          }
                               },
                },
                'required': ['task_id', 'fields'],
            },
        },
        responses={
            200: OpenApiResponse(
                description="Field created successfully",
                examples={
                    'application/json': {
                        'task': {
                            'id': 'string',
                            'task_id': 'string',
                            'user_id': 'string',
                            'created_at': 'string',
                            'updated_at': 'string',
                            'fields': [
                                {'type': 'object',
                                 'properties': {
                                     'id': {'type': 'string'},
                                     'type': {'type': 'string'},
                                     'name': {'type': 'string'},
                                     'content': {'type': 'string'},
                                 }
                                 }
                            ],
                        }
                    }
                }
            ),
            500: OpenApiResponse(description="Internal Server Error"),
        },
    )
    def post(self, request, *args, **kwargs):
        task_id = request.data.get('task_id')
        try:
            print([TaskFieldModel(name=i.get("name"), _type=i.get("type"),
                                  content=i.get("content")).to_dict() for i in request.data.get('fields')])

            field = create_or_update_field(request.user.id, task_id,
                                           [TaskFieldModel(name=i.get("name"), _type=i.get("type"),
                                                           content=i.get("content")) for i in
                                            request.data.get('fields')])
            return Response(field.to_dict(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'task_id': {'type': 'string'},
                    'created_at': {'type': 'string'},
                    'updated_at': {'type': 'string'},
                    'fields': {'type': 'array', 'items': {'type': 'object',
                                                          'properties': {
                                                              'id': {'type': 'string'},
                                                              'type': {'type': 'string'},
                                                              'name': {'type': 'string'},
                                                              'content': {'type': 'string'},
                                                          }
                                                          }
                               },
                },
                'required': ['task_id', 'fields'],
            },
        },
        responses={
            200: OpenApiResponse(
                description="Field created successfully",
                examples={
                    'application/json': {
                        'task': {
                            'id': 'string',
                            'task_id': 'string',
                            'user_id': 'string',
                            'created_at': 'string',
                            'updated_at': 'string',
                            'fields': [
                                {'type': 'object',
                                 'properties': {
                                     'id': {'type': 'string'},
                                     'type': {'type': 'string'},
                                     'name': {'type': 'string'},
                                     'content': {'type': 'string'},
                                 }
                                 }
                            ],
                        }
                    }
                }
            ),
            500: OpenApiResponse(description="Internal Server Error"),
        },
    )
    def put(self, request, *args, **kwargs):
        """
        TO-DO field multiple
        """
        task_id = request.data.get('task_id')
        try:
            field = update_field(updater_user=request.user,user_id=request.user.id, task_id=task_id,
                                 fields=[TaskFieldModel(_id=i.get("id"), name=i.get("name"), _type=i.get("type"),
                                                        content=i.get("content")) for i in
                                         request.data.get('fields')]
                                 )

            return Response(field.to_dict(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FieldIdView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NoOpSerializer


    def get(self, request, task_id, *args, **kwargs):
        try:
            found_fields = get_fields_by_user_id_task_id(user_id=request.user.id, task_id=task_id)
            return Response([found_field.to_dict() for found_field in found_fields], status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, task_id, *args, **kwargs):
        try:
            delete_field(user_id=request.user.id, task_id=task_id)
            return Response({"deleted"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
