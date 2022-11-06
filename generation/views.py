from rest_framework.views import APIView
from rest_framework import permissions
from utils.process_files import process_uploaded_zip
from rest_framework.response import Response
from django.conf import settings
import os, shutil


class GenerationView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        GENERATIONS_FOLDER = "generations/"
        GENERATIONS_READY_FOLDER = "ready/"
        user = request.user

        try:
            file_obj = request.data["file"]
        except KeyError:
            return Response({"error": "File does not exist"}, status=400)
        # user = request.user
        # form_data = request.data['formData']
        print(request.data)

        dir_path = settings.MEDIA_ROOT + "/" + user.username + "/" + GENERATIONS_FOLDER
        web_path = settings.MEDIA_URL[1:] + user.username + "/" + GENERATIONS_FOLDER

        zip_file, _ = process_uploaded_zip(file_obj)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            shutil.rmtree(dir_path)
            os.makedirs(dir_path)

        zip_file.extractall(path=dir_path)
        zip_file.close()

        # инициальзируем класс, получаем путь к файлу
