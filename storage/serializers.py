from email.policy import default
from rest_framework import serializers
from .models import AuthUploadedFile

class AuthUploadedFileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')

    class Meta:
        model = AuthUploadedFile
        fields = ("user", )