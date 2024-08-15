from django.db import models
from company.models import Company, Employee

# Create your models here.
class File(models.Model):
    name = models.CharField(default="", max_length=255)
    suffix = models.CharField(default="", max_length=255)

    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='files_created')
    updated_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='files_updated')
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='files_user')

    file = models.FileField()
