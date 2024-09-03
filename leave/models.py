from django.db import models

from company.models import Employee


# Create your models here.


class Leave(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    manager_user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='manager_leave_requests')

    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()

    total_days = models.IntegerField()

    status = models.CharField(default=False)

