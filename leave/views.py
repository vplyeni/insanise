import math
from datetime import date, timedelta, datetime

from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from leave.models import Leave
from leave.serializers import LeaveSerializer
from mailer import mailer


# Create your views here.


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='skip', description='Number of items to skip', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='limit', description='Maximum number of items to return', required=False,
                             type=OpenApiTypes.INT),
        ],
    )
    def list(self, request, *args, **kwargs):
        skip = self.request.query_params.get('limit', 0)
        limit = self.request.query_params.get('limit', 5)

        leaves = self.queryset.filter(user_id=request.user.id)[skip:limit + skip]
        count = self.queryset.filter(user_id=request.user.id).count()

        serialized_leaves = self.serializer_class(leaves, many=True)

        return Response({'data': serialized_leaves.data, 'count': count}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    @extend_schema(
        parameters=[
            OpenApiParameter(name='skip', description='Number of items to skip', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='limit', description='Maximum number of items to return', required=False,
                             type=OpenApiTypes.INT),
        ],
    )
    def waiting_for_approve(self, request, *args, **kwargs):
        skip = self.request.query_params.get('limit', 0)
        limit = self.request.query_params.get('limit', 5)

        leaves = self.queryset.filter(manager_user=request.user.id)[skip:limit + skip]
        count = self.queryset.filter(manager_user=request.user.id).count()

        serialized_leaves = self.serializer_class(leaves, many=True)

        return Response({'data': serialized_leaves.data, 'count': count}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        if not hasattr(data, 'start_date'):
            data["start_date"] = str(date.today() + timedelta(days=1))

        if not hasattr(data, 'end_date'):
            data["end_date"] = str(date.today() + timedelta(days=2))

        date_format = "%Y-%m-%d"

        start_date = datetime.strptime(data["start_date"], date_format)
        end_date = datetime.strptime(data["end_date"], date_format)

        if start_date > end_date:
            return Response({"error": "Start date must be before end date"}, status=status.HTTP_400_BAD_REQUEST)

        if start_date == end_date:
            return Response({"error": "End date cannot be the same"}, status=status.HTTP_400_BAD_REQUEST)

        if datetime.now() >= start_date:
            return Response({"error": "Start date cannot be in the past"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the difference
        time_diff = end_date - start_date

        # Get the total difference in hours (or any other unit like days, minutes, etc.)
        days_diff = time_diff.total_seconds() / (3600*24)# converting seconds to hours

        # Round up
        rounded_days = math.ceil(days_diff)

        data['manager_user'] = user.manager_user.id
        data['user'] = user.id
        data['total_days'] = rounded_days
        data['status'] = "Requested"

        serialized_leave = self.serializer_class(data=request.data)

        if serialized_leave.is_valid(raise_exception=True):
            serialized_leave.save()



            return Response(serialized_leave.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"])
    @extend_schema(
        parameters=[
            OpenApiParameter(name='approve', description='Number of items to skip', required=True, type=OpenApiTypes.INT),
        ],
    )
    def approve_leave(self, request, *args, **kwargs):
        approve_id = self.request.query_params.get('approve', 0)

        if approve_id == 0:
            return Response({"error": "Approval id is required"}, status=status.HTTP_400_BAD_REQUEST)

        leave = Leave.objects.get(id=approve_id)
        if leave is None:
            return Response({"error": "Leave does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if leave.status != "Requested":
            return Response({"error": "Leave is not in Requested Status."}, status=status.HTTP_400_BAD_REQUEST)

        if leave.manager_user != request.user.id:
            return Response({"error": "You do not have permission to approve leave"}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = "Approved"
        leave.save()

        start_date = str(leave.start_date)
        end_date = str(leave.end_date)

        employee = leave.user
        manager = leave.manager_user

        content = str('Dear ' + employee.first_name + " " + employee.last_name + ",\n \n"
                      + "Your manager " + manager.first_name + " " + manager.last_name
                      + " has approved your leave.\n \n"
                      + "Dates: " + str(start_date) + " - " + str(end_date))
        mailer.send(employee.email, "Your Manager Has Approved your Leave", content)

        content = str('Dear ' + manager.first_name + " " + manager.last_name + ",\n \n"
                      + "You successfully approved leave for your employee "
                      + employee.first_name + " " + employee.last_name + ".\n \n" + "Dates: "
                      + str(start_date) + " - " + str(end_date))
        mailer.send(manager.email, "You Approved a Leave for your Employee", content)

        return Response(leave, status=status.HTTP_200_OK)

    def decline_leave(self, request, *args, **kwargs):
        decline_id = self.request.query_params.get('approve', 0)

        if decline_id == 0:
            return Response({"error": "Approval id is required"}, status=status.HTTP_400_BAD_REQUEST)

        leave = Leave.objects.get(id=decline_id)
        if leave is None:
            return Response({"error": "Leave does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if leave.status == "Approved" or leave.status == "Declined" or leave.status == "Withdrawn":
            return Response({"error": "Leave is already approved or declined or withdrawn"}, status=status.HTTP_400_BAD_REQUEST)

        if leave.manager_user != request.user.id:
            return Response({"error": "You do not have permission to approve leave"}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = "Declined"
        leave.save()

        start_date = str(leave.start_date)
        end_date = str(leave.end_date)

        employee = leave.user
        manager = leave.manager_user

        content = str('Dear ' + employee.first_name + " " + employee.last_name + ",\n \n"
                      + "Your manager " + manager.first_name + " " + manager.last_name
                      + " has declined your leave.\n \n"
                      + "Dates: " + str(start_date) + " - " + str(end_date))
        mailer.send(employee.email, "Your Manager Has Declined your Leave", content)

        content = str('Dear ' + manager.first_name + " " + manager.last_name + ",\n \n"
                      + "You successfully declined leave for your employee "
                      + employee.first_name + " " + employee.last_name + ".\n \n" + "Dates: "
                      + str(start_date) + " - " + str(end_date))
        mailer.send(manager.email, "You Declined a Leave for your Employee", content)

        return Response(leave, status=status.HTTP_200_OK)

    def withdraw_leave(self, request, *args, **kwargs):
        withdraw_id = self.request.query_params.get('approve', 0)

        if withdraw_id == 0:
            return Response({"error": "Approval id is required"}, status=status.HTTP_400_BAD_REQUEST)

        leave = Leave.objects.get(id=withdraw_id)
        if leave is None:
            return Response({"error": "Leave does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if leave.manager_user != request.user.id:
            return Response({"error": "You do not have permission to approve leave"}, status=status.HTTP_400_BAD_REQUEST)
        if leave.status == "Approved" or leave.status == "Declined" or leave.status == "Withdrawn":
            return Response({"error": "Leave is already approved or declined or withdrawn"}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = "Withdrawn"
        leave.save()

        employee = leave.user
        manager = leave.manager_user

        start_date = str(leave.start_date)
        end_date = str(leave.end_date)

        content = str('Dear ' + employee.first_name + " " + employee.last_name + ",\n \n"
                      + "You successfully " + manager.first_name + " " + manager.last_name
                      + " withdraw your leave.\n \n"
                      + "Dates: " + str(start_date) + " - " + str(end_date))

        mailer.send(employee.email, "Your Leave Request Successfully withdrawn", content)

        content = str('Dear ' + manager.first_name + " " + manager.last_name + ",\n \n"
                      + "Your employee" + employee.first_name + " " + employee.last_name
                      + " withdraw their leave.\n \n" + "Dates: "
                      + str(start_date) + " - " + str(end_date))
        mailer.send(manager.email, "Your Employee Withdraw their Leave Request", content)

        return Response(leave, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        user = request.user

        data = request.data

        if not "start_date" in data.keys():
            data["start_date"] = str(date.today() + timedelta(days=1))

        if not "end_date" in data.keys():
            data["end_date"] = str(date.today() + timedelta(days=2))

        date_format = "%Y-%m-%d"

        start_date = datetime.strptime(data["start_date"], date_format)
        end_date = datetime.strptime(data["end_date"], date_format)

        if start_date > end_date:
            return Response({"error": "Start date must be before end date"}, status=status.HTTP_400_BAD_REQUEST)

        if start_date == end_date:
            return Response({"error": "End date cannot be the same"}, status=status.HTTP_400_BAD_REQUEST)

        if datetime.now() >= start_date:
            return Response({"error": "Start date cannot be in the past"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the difference
        time_diff = end_date - start_date

        # Get the total difference in hours (or any other unit like days, minutes, etc.)
        days_diff = time_diff.total_seconds() / (3600 * 24)  # converting seconds to hours

        # Round up
        rounded_days = math.ceil(days_diff)

        leave = Leave.objects.get(id=pk)

        if leave is None:
            return Response({"error": "Leave does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if leave.status == "Approved" or leave.status == "Declined" or leave.status == "Withdrawn":
            return Response({"error": "Leave is already approved or declined or withdrawn"}, status=status.HTTP_400_BAD_REQUEST)

        if leave.manager_user_id == request.user.id:
            manager = leave.manager_user
            employee = leave.user
            leave.status = "Offered"
            leave.start_date = start_date
            leave.end_date = end_date
            leave.save()

            content = str('Dear ' + employee.first_name + " " + employee.last_name + ",\n \n"
                          + "Your manager " + manager.first_name + " " + manager.last_name
                          + " has offered a new date for your leave.\n \n"
                          + "New Dates: " + str(start_date) + " - " + str(end_date))
            mailer.send(employee.email, "Your Manager Has Offered a new Leave Date", content)

            content = str('Dear ' + manager.first_name + " " + manager.last_name + ",\n \n"
                          + "You successfully offered a new leave date for your employee "
                          + employee.first_name + " " + employee.last_name + ".\n \n" + "New Dates: "
                          + str(start_date) + " - " + str(end_date))
            mailer.send(manager.email, "You Offered a new Leave Date for your Employee", content)

            return Response({"offered"}, status=status.HTTP_200_OK)
        elif leave.user_id == request.user.id:
            leave.status = "Requested"
            leave.start_date = start_date
            leave.end_date = end_date
            leave.save()

            employee = leave.user
            manager = leave.manager_user

            content = str('Dear ' + manager.first_name + " " + manager.last_name + ",\n \n"
                          + "You successfully requested a new leave date "
                          + employee.first_name + " " + employee.last_name + ".\n \n" + "New Dates: "
                          + str(start_date) + " - " + str(end_date))


            mailer.send(employee.email, "You successfully Has Requested a new Leave Date", content)

            content = str('Dear ' + employee.first_name + " " + employee.last_name + ",\n \n"
                          + "Your employee " + manager.first_name + " " + manager.last_name
                          + " has requested a new date for their leave.\n \n"
                          + "New Dates: " + str(start_date) + " - " + str(end_date))

            mailer.send(manager.email, "Your Employee Requested a new Leave Date", content)


            return Response(leave, status=status.HTTP_200_OK)
        else:
            return Response({"error":"You do not have permission to approve leave"}, status=status.HTTP_400_BAD_REQUEST)
