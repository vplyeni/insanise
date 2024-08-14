from django.urls import path, include

from harmonise.views import TaskView, TaskListView, FieldIdView, FieldView

urlpatterns = [
    path('task/', TaskListView.as_view(), name='harmonise'),
    path('task/<str:_id>/', TaskView.as_view(), name='harmonise'),
    path('field/', FieldView.as_view(), name='harmonise'),
    path('field/<str:task_id>/', FieldIdView.as_view(), name='harmonise'),
]
