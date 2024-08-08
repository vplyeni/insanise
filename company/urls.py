# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, TargetGroupViewSet, TeamViewSet, EmployeeViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'target_groups', TargetGroupViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'employees', EmployeeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
