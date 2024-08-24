from django.urls import path, include
from rest_framework.routers import DefaultRouter

from harmonise.views import (TaskView, TaskListView, TaskUserListView,
                             TaskUserView, FileView, ManagerTaskViewSet)

router = DefaultRouter()
router.register(r'', ManagerTaskViewSet, basename='manager-task')

urlpatterns = [
    path('task/manager/', include(router.urls)),
    path('task/', TaskListView.as_view(), name='task_list'),
    path('task/<str:_id>/', TaskView.as_view(), name='task'),
    path('task_user/file/', FileView.as_view(), name='field_files'),
    #    path('task_user/', TaskUserListView.as_view(), name='task_user_list'),
    #    path('task_user/<str:task_id>', TaskUserView.as_view(), name='task_user'),
]
