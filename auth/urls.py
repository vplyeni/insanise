from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from auth.views import EmployeeAuthViewSet

router = DefaultRouter()
router.register(r'', EmployeeAuthViewSet, basename='manager-task')
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/test/', TokenVerifyView.as_view(), name='validate_token'),
    path('user/', include(router.urls)),

]