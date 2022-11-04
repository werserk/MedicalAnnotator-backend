from datetime import datetime
from io import BytesIO
import zipfile, os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from accounts.models import UserAccount

from .models import Study
from django.conf import settings
from wsgiref.util import FileWrapper
from django.http import HttpResponse
import pydicom
import numpy as np

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
    
    try:
        instance_id = data[("0020", "000E")].value
    except KeyError:
        instance_id = "-"

    return name, modality, done, patient_id, instance_id
    

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
        file = file_obj.read()

        try:
            if file_obj.name != "blob" and file_obj.name.split(".")[-1] != "zip":
                try:
                    name, modality, done, patient_id, instance_id = parse_dicom(file)
                except Exception:
                    return Response({"error": "Can't read dicom tags"}, status=400)
                path = dir_path + str(patient_id) + "/" + str(instance_id) + "/"
                if not os.path.exists(path):
                    os.makedirs(path)
                elif os.path.isfile(path + file_obj.name):
                    return Response({"error": "Вы уже загружали это исследование"}, status=400)
                with open(path + file_obj.name, "wb") as f:
                    f.write(file)
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
                    return Response({"error": "Пустой архив"}, status=400)
                try:
                    name, modality, done, patient_id, instance_id = parse_dicom(buffer)
                    if name == "-":
                        return Response({"error": "Исследование не имеет имени"}, status=400)
                except Exception:
                    return Response({"error": "Не удалось прочитать информацию из дайкома"}, status=400)
                path = dir_path + str(patient_id) + "/" + str(instance_id) + "/"
                if os.path.isdir(path):
                    return Response({"error": "Вы уже загружали это исследование"}, status=400)
                new_zip.extractall(path=path)
                new_zip.close()
            study = Study(done=done, name=name, modality=modality, user=user, patient_id=patient_id, instance_id=instance_id)
            study.save()
            return Response({"success": "Successfully uploaded"}, status=200)
        except Exception:
            Response({"error": "Не смогли загрузить файл"}, status=500)


def get_axial_slice(image, ind):
    return image[ind, :, :]


def get_coronal_slice(image, ind):
    return image[:, ind, :]


def get_saggital_slice(image, ind):
    return image[:, :, ind]


def get_my_slices(array, idx, axis=0):
    window_width = 10
    left_idx = min(idx - window_width, 0)
    right_idx = max(idx + window_width, array.shape[axis])
    for i in range(left_idx, right_idx + 1):
        if axis == 0:
            yield get_axial_slice(array, i)
        elif axis == 1:
            yield get_coronal_slice(array, i)
        elif axis == 2:
            yield get_saggital_slice(array, i)


def slice_survey(paths, idx, axis=0):
    for path in paths:
        single_slice = pydicom.dcmread(path)
        array.append(single_slice.pixel_array)
    array = np.array(array)
    image = get_my_slices(array, idx, axis)


class StudyProcessingView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None, **kwargs):
        user = request.user
        study = user.study_set.get(unique_id=kwargs["unique_id"])

        path = settings.MEDIA_ROOT + "/" + user.username + "/" + study.patient_id + "/" + study.instance_id + "/"
        web_path = user.username + "/" + study.patient_id + "/" + study.instance_id

        file_names = os.listdir(path)
        paths = [path + file_name for file_name in file_names]

        slices_paths = slice_survey(paths, idx=0)

        return Response({"paths": [slices_paths]})
    

    def patch(self, request, format=None, **kwargs):
        user = request.user
        try:
            study = user.study_set.get(unique_id=kwargs["unique_id"])
        except Study.DoesNotExist:
            return Response({"error": "Исследование не найдено"}, status=400)
        study.comment = request.data['comment']
        study.save()
        return Response({"success": "Комментарий успешно обновлен"})
    
    def delete(self, request, format=None, **kwargs):
        user = request.user
        try:
            study = user.study_set.get(unique_id=kwargs["unique_id"])
        except Study.DoesNotExist:
            return Response({"error": "Исследование не найдено"}, status=400)
        study.delete()
        return Response({"success": "Комментарий успешно удален"})


class GetDicomEndpoint(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None):
        path = request.GET.get("path", "")
        if path:
            path = settings.MEDIA_ROOT + "/" + path
            name = path.split("/")[-1]

            file = open(path, 'rb')
            response = HttpResponse(FileWrapper(file), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="%s"' % name
            return response
        return Response({"error": "Некоректный параметр запроса"})


class StudyListView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None, **kwargs):
        if "unique_id" in kwargs:
            try:
                user = UserAccount.objects.get(unique_id=kwargs["unique_id"])
            except UserAccount.DoesNotExist:
                return Response({"error": "Пользователь не найден"})
        else:
            user = request.user
        studies = user.study_set.all()
        data = []
        for study in studies:
            data.append({
                "unique_id": study.unique_id,
                "series_id": study.instance_id,
                "patient_id": study.patient_id,
                "date_upload": study.date_upload.strftime("%m.%d.%Y"),
                "date_study": study.done,
                "modality": study.modality,
                "state": study.state,
                "comment": study.comment,
                "name": study.name})
        return Response(data, status=200)