from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from auth import views

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/test/', TokenVerifyView.as_view(), name='validate_token'),
    path('user/me/', views.EmployeeProfileView.as_view(), name='me_employee_profile'),

]