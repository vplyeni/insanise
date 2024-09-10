from django.db import models


# Create your models here.
class Mail(models.Model):
    subject = models.CharField(max_length=255)
    from_email = models.CharField(max_length=255)
    to_email = models.CharField(max_length=255)
    body = models.TextField()

    date = models.DateTimeField()

    def __str__(self):
        return self.subject + " - " + self.body
