from django.urls import path, include

from harmonise.views import (TaskView, TaskListView, TaskUserListView,
                             TaskUserDetailView, FileView, AllTasksView)


urlpatterns = [
    path('task/', TaskListView.as_view(), name='harmonise'),
    path('task/<str:_id>/', TaskView.as_view(), name='harmonise'),
    path('task_all/', AllTasksView.as_view(), name='harmonise'),
    path('field_files/', FileView.as_view(), name='field_files'),
    path('task_user/', TaskUserListView.as_view(), name='harmonise'),
    path('task_user/<str:task_id>', TaskUserDetailView.as_view(), name='harmonise'),
]
