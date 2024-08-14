from django.urls import path, include

from harmonise.views import TaskView, TaskListView,UserFieldListView, UserFieldDetailView

urlpatterns = [
    path('task/', TaskListView.as_view(), name='harmonise'),
    path('task/<str:_id>/', TaskView.as_view(), name='harmonise'),
    path('user_field/', UserFieldListView.as_view(), name='harmonise'),
    path('user_field/<str:task_id>', UserFieldDetailView.as_view(), name='harmonise'),
]
