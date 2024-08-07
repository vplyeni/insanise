from django.db import models

from company.models import TargetGroup, Team, Employee


# Create your models here.
class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_notified = models.BooleanField(default=False)
    should_notify = models.BooleanField(default=False)

    assigned_target_group = models.ForeignKey(TargetGroup, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"


class TaskEmployee(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.task.name + " - " + self.employee.first_name + " " + self.employee.last_name

    class Meta:
        verbose_name = "Task Employee"
        verbose_name_plural = "Task Employees"


class Field(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Field"
        verbose_name_plural = "Fields"


class FieldEmployee(models.Model):
    employee = models.ForeignKey(Employee, null=False, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, null=False, on_delete=models.CASCADE)
    task = models.ForeignKey(TaskEmployee, null=False, on_delete=models.CASCADE)

    type = models.IntegerField()
    content = models.TextField()

    def __str__(self):
        return self.field.name + " - " + self.content

    class Meta:
        verbose_name = "Field Employee"
        verbose_name_plural = "Field Employees"
