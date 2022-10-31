from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.timezone import now
import uuid

from storage.models import Study


class UserAccount(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    username = models.CharField(max_length=255, unique=True)
    last_login = models.DateTimeField(default=now, blank=True)
    studies = models.ForeignKey(Study, on_delete=models.CASCADE)

    def create_user(self, username, password=None):
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(username=username)
        user.is_active = True

        user.set_password(password)
        user.save()

        return user  

    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username


class SuperUserAccount(UserAccount):
    users = models.ForeignKey(UserAccount, on_delete=models.CASCADE)

    def create_user(self, username, password):
        user = self.create_user(username, password)

        user.is_superuser = True
        user.save()

        return user  
