from rest_framework import serializers
from .models import Study, Instance

class StudyViewSetSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')

    class Meta:
        model = Study
        fields = ("name", )


class InstanceViewSetSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')

    class Meta:
        model = Instance
        fields = ("name", )