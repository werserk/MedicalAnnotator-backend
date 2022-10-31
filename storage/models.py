from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Study(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Instance(models.Model):
    FILE_UPLOAD_TYPES = [("DIR", "Directory"), ("FILE", "File")]
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    upload_type = models.CharField(max_length=4, choices=FILE_UPLOAD_TYPES, default="FILE",)

    def __str__(self):
        return self.name