import django
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, UserManager
from django.utils.timezone import now
import uuid

class MyUserManager(UserManager):
    def create_user(self, username, password):
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(username=username)
        user.is_active = True

        user.set_password(password)
        user.save()

        return user

    def create_advanced_user(self, username, password):
        user = self.create_user(username, password)

        superuser = SuperUser(related_user=user)
        user.is_advanced = True
        superuser.save()
        user.save()
        
        return superuser
        
    def create_common_user(self, username, password=None):
        user = self.create_user(username, password)

        common_user = User(related_user=user)
        common_user.save()

        return common_user


class UserAccount(AbstractUser, PermissionsMixin):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=255, unique=True)
    is_advanced = models.BooleanField(default=False)
    studies_completed = models.IntegerField(default=0)
    
    objects = MyUserManager()

    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username
    

class User(models.Model):
    related_user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)

    def __str__(self):
        return self.related_user.username


class SuperUser(models.Model):
    related_user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name="users", blank=True)

    def __str__(self):
        return self.related_user.username
