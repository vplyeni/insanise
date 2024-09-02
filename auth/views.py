from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import EmployeeAuthSerializer, NoOpSerializer, EmployeeChangePasswordSerializer


class EmployeeAuthViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeAuthSerializer

    @action(methods=["GET"], detail=False)
    def me(self, request):
        employee = request.user
        serializer = self.serializer_class(employee)
        return Response(serializer.data)

    @action(methods=["PATCH"], detail=False, serializer_class=EmployeeChangePasswordSerializer)
    def change_password(self, request):
        try:
            employee = request.user
            serializer = self.serializer_class(request.data)

            if employee.check_password(serializer.data['current_password']):
                employee.set_password(serializer.data['new_password'])
                employee.save()
            else:
                return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Password Changed'}, status=status.HTTP_200_OK)


