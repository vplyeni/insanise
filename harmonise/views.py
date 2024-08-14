from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiParameter
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from mongocon.mongo_models import Task, TaskFieldModel, TaskFieldTypeModel
from .serializers import NoOpSerializer

import json
# Create your views here.


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
            tasks = Task.objects(assigned_to__contains=request.user.id)[skip:limit+skip]
            count = Task.objects(assigned_to__contains=request.user.id).count()
            print(tasks)
            return Response({'data': json.loads(tasks.to_json()), 'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)