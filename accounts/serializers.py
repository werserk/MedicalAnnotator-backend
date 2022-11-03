from rest_framework import serializers
from .models import SuperUser

class UsersListViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuperUser
        fields = ("id", "username", "last_login")