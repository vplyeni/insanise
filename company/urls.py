# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

import leave
from .views import CompanyViewSet, TargetGroupViewSet, TeamViewSet, EmployeeViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='companies')
router.register(r'target_groups', TargetGroupViewSet, basename='target_groups')
router.register(r'teams', TeamViewSet, basename='teams')
router.register(r'employees', EmployeeViewSet, basename='employees')

urlpatterns = [
    path('leave/', include('leave.urls')),
    path('', include(router.urls)),
]
