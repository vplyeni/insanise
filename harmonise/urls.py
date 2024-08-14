from django.urls import path, include

from harmonise.views import TaskView

urlpatterns = [
    path('task/', TaskView.as_view(), name='harmonise'),
]