from django.urls import include, path
from rest_framework import routers

from leave.views import LeaveViewSet

router = routers.DefaultRouter()
router.register(r'', LeaveViewSet, basename='leaves')

urlpatterns = [
    path('', include(router.urls)),
]