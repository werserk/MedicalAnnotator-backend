from rest_framework import serializers
from .models import Study, Instance

class StudyViewSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Study
        fields = ("name", )


class InstanceViewSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Instance
        fields = ("name", )