from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from leave.models import Leave


# Create your views here.


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()

    def list(self, request, *args, **kwargs):
        skip = self.request.query_params.get('limit', 0)
        limit = self.request.query_params.get('limit', 5)

        return Response("", status=status.HTTP_200_OK)


    """
    Fundamentals
    """
    def create(self, request, *args, **kwargs):
        return Response("", status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def approve_leave(self, request, *args, **kwargs):
        return Response("", status=status.HTTP_200_OK)
