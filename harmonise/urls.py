from django.urls import path, include
from rest_framework.routers import DefaultRouter

from harmonise.views import (TaskListView, TaskUserListView,
                             TaskUserView, FieldView, ManagerTaskViewSet)

router = DefaultRouter()
router.register(r'', ManagerTaskViewSet, basename='manager-task')


field_router = DefaultRouter()
field_router.register(r'', FieldView, basename='manager-task')

urlpatterns = [
    path('task/manager/', include(router.urls)),
    path('task_user/', include(field_router.urls), name='field'),
    path('task/', TaskListView.as_view(), name='task_list'),

    #    path('task_user/', TaskUserListView.as_view(), name='task_user_list'),
    #    path('task_user/<str:task_id>', TaskUserView.as_view(), name='task_user'),
]
