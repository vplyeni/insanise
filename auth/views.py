from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import EmployeeAuthSerializer, NoOpSerializer


class EmployeeProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeAuthSerializer

    def get(self, request):
        employee = request.user
        serializer = self.serializer_class(employee)
        return Response(serializer.data)


class EmployeeChangePassword(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeAuthSerializer

    def post(self, request):
        employee = request.user
        serializer = self.serializer_class(employee)
        return Response(serializer.data)
