from django.db import models
from django.contrib.auth.models import AbstractUser


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    # Define fields
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    founded_date = models.DateField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Contact information
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    # Company details
    industry = models.CharField(max_length=100, blank=True, null=True)
    number_of_employees = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Meta options (optional)
    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class TargetGroup(models.Model):
    id = models.AutoField(primary_key=True)
    # Define fields
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # ForeignKey fields
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Target Group"
        verbose_name_plural = "Target Groups"

    def __str__(self):
        return self.name


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    # Define fields
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # ForeignKey fields
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self):
        return self.name


class Employee(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    # Additional fields for Employee
    position = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    is_manager = models.BooleanField(default=False)

    is_lead = models.BooleanField(default=False)

    manager_user = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='direct_reports', null=True,
                                     blank=True)
    # ForeignKey fields
    company = models.ForeignKey(Company, null=True, blank=True,on_delete=models.CASCADE)
    target_group = models.ForeignKey(TargetGroup, null=True, blank=True, on_delete=models.SET_NULL)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
