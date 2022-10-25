import zipfile, io, os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import AuthUploadedFile
from django.conf import settings


class FileUploadView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request, format=None):
        try:
            file_obj = request.FILES['file']
        except KeyError:
            return Response({"error": "File does not exist"}, status=400)

        user = self.request.user

        try:
            latest_id = str(AuthUploadedFile.objects.latest("id").id)
            dirname = latest_id.rjust(10, "0")
        except AuthUploadedFile.DoesNotExist:
            dirname = "0" * 9 + "1"

        path = settings.MEDIA_ROOT + "/" + user.username + "/" + dirname + "/"

        if not os.path.exists(path):
            os.makedirs(path)
        try:
            print(file_obj.name.split(".")[-1])
            if file_obj.name != "blob" and file_obj.name.split(".")[-1] != "zip":
                with open(path + file_obj.name, "wb") as f:
                    f.write(file_obj.read())
                    AuthUploadedFile(user=user).save()
            else:
                with zipfile.ZipFile(file_obj, 'r') as zip_ref:
                    zip_ref.extractall(path=path)
            return Response({"success": "Succesfully uploaded"}, status=200)
        except TypeError:
            Response({"error": "Can't save file"}, status=500)