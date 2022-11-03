from datetime import datetime
from io import BytesIO
import zipfile, os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .models import Study
from django.conf import settings
from wsgiref.util import FileWrapper
from django.http import HttpResponse
import pydicom

# # TODO: processing mult files

def parse_dicom(file):
    data = pydicom.dcmread(BytesIO(file))
    try:
        name = data[("0010", "0010")].value
    except KeyError:
        name = "-"
    try:
        modality = data[("0008", "0060")].value
    except KeyError:
        modality = "-"

    try:
        done = data[("0008", "0021")].value
        done = done[0:4] + "." + done[4:6] + "." + done[6:8]
    except KeyError:
        done = "-"

    try:
        patient_id = data[("0010", "0020")].value
    except KeyError:
        patient_id = "-"

    return name, modality, done, patient_id
    

class FileUploadView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request, format=None):
        user = request.user
        try:
            file_obj = request.FILES['file']
        except KeyError:
            return Response({"error": "File does not exist"}, status=400)

        user = self.request.user
        dir_path = settings.MEDIA_ROOT + "/" + user.username + "/" 

        try:
            if file_obj.name != "blob" and file_obj.name.split(".")[-1] != "zip":
                try:
                    name, modality, done, patient_id = parse_dicom(file_obj.read())
                    if name == "-":
                        return Response({"error": "Исследование не имеет имени"}, status=400)
                except Exception:
                    return Response({"error": "Can't read dicom tags"}, status=400)
                path = dir_path + str(name) + "/"
                if not os.path.exists(path):
                    os.makedirs(path)
                with open(path + file_obj.name, "wb") as f:
                    f.write(file_obj.read())
            else:
                original_zip = zipfile.ZipFile(file_obj, 'r')
                new_zip = zipfile.ZipFile(file_obj.name, 'w')
                for item in original_zip.infolist():
                    buffer = original_zip.read(item.filename)
                    if not str(item.filename).startswith('__MACOSX/'):
                        new_zip.writestr(item, buffer)
                original_zip.close()
                if new_zip.namelist():
                    file_obj.name = new_zip.namelist()[0]
                else:
                    return Response({"error": "Пустой архив"})
                try:
                    name, modality, done, patient_id = parse_dicom(buffer)
                    if name == "-":
                        return Response({"error": "Исследование не имеет имени"}, status=400)
                except Exception:
                    return Response({"error": "Не удалось прочитать информацию из дайкома"}, status=400)
                path = dir_path + str(name) + "/"
                print(os.path.isdir(path))
                if os.path.isdir(path):
                    return Response({"error": "Вы уже загружали это исследование"}, status=400)
                new_zip.extractall(path=path)
                new_zip.close()
            Study(done=done, name=name, modality=modality, user=user, patient_id=patient_id).save()
            return Response({"success": f"Successfully uploaded"}, status=200)
        except Exception:
            Response({"error": "Не смогли загрузить файл"}, status=500)


class StudyProcessingView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None, **kwargs):
        user = request.user
        study = user.study_set.get(unique_id=kwargs["unique_id"])

        path = settings.MEDIA_ROOT + "/" + user.username + "/" + study.name + "/"
        if os.path.isfile(path + study.name):
            file = open(path + study.name, 'rb')
            response = HttpResponse(FileWrapper(file), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="%s"' % study.name
            return response
        else:
            file_names = os.listdir(settings.MEDIA_ROOT + "/" + user.username + "/" + study.name + "/")
            web_paths = []
            for name in file_names:
                web_paths.append(settings.MEDIA_URL + user.username + "/" + study.name + "/" + name)
            return Response({"file": web_paths})


class StudyListView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None):
        return Response(request.user.study_set.all().values())