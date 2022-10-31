import zipfile, os
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import permissions
from .models import Instance, Study
from django.conf import settings
from wsgiref.util import FileWrapper
from django.http import HttpResponse
from .serializers import StudyViewSetSerializer, InstanceViewSetSerializer

# TODO: processing mult files

class FileUploadView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request, format=None):
        try:
            file_obj = request.FILES['file']
        except KeyError:
            return Response({"error": "File does not exist"}, status=400)

        user = self.request.user

        try:
            latest_id = str(Study.objects.latest("id").id)
            dirname = latest_id.rjust(10, "0")
        except Study.DoesNotExist:
            dirname = "0" * 10

        path = settings.MEDIA_ROOT + "/" + user.username + "/" + dirname + "/"
        study = Study(name=dirname, user=user)
        instance_name = "".join(file_obj.name.split(".")[:-1])

        if not os.path.exists(path):
            os.makedirs(path)
        try:
            if file_obj.name != "blob" and file_obj.name.split(".")[-1] != "zip":
                with open(path + file_obj.name, "wb") as f:
                    f.write(file_obj.read())
                    study.save()
                    Instance(name=instance_name, study=study).save()
            else:
                original_zip = zipfile.ZipFile(file_obj, 'r')
                new_zip = zipfile.ZipFile(file_obj.name, 'w')
                for item in original_zip.infolist():
                    buffer = original_zip.read(item.filename)
                    if not str(item.filename).startswith('__MACOSX/'):
                        new_zip.writestr(item, buffer)
                original_zip.close()
                new_zip.extractall(path=path)
                new_zip.close()
                study.save()
                Instance(name=instance_name, study=study).save()
                study.save()
            return Response({"success": f"Succesfully uploaded {file_obj.name}"}, status=200)
        except TypeError:
            Response({"error": "Can't save file"}, status=500)


class StudyViewSet(ReadOnlyModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudyViewSetSerializer
    permission_classes = (permissions.IsAuthenticated, )
    
    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

class InstanceViewSet(ReadOnlyModelViewSet):
    queryset = Instance.objects.all()
    serializer_class = InstanceViewSetSerializer
    permission_classes = (permissions.IsAuthenticated, )
    
    def get_queryset(self, **kwargs):
        user = self.request.user
        study = Study.objects.get(name=self.kwargs["study"], user=user)
        queryset = self.queryset.filter(study=study)
        return queryset

class InstanceProcessingView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None, **kwargs):
        user = self.request.user
        study_name = kwargs["dirName"]
        instance_name = kwargs["instanceName"]
        try:
            study = Study.objects.get(name=study_name)
        except IndexError:
            return Response({"error": "study does not exist"})
        try:
            instance = Instance.objects.get(study=study, name=instance_name)
        except IndexError:
            return Response({"error": "instance does not exist"})
        path = settings.MEDIA_ROOT + "/" + user.username + "/" + study_name + "/"
        file_name = os.listdir(path)[0]
        if os.path.isfile(path + file_name):
            file = open(path + file_name, 'rb')
            response = HttpResponse(FileWrapper(file), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
            return response
        else:
            file_names = os.listdir(settings.MEDIA_ROOT + "/" + user.username + "/" + study_name + "/")
            web_paths = []
            for name in file_names:
                web_paths.append(settings.MEDIA_URL + user.username + "/" + study_name + "/" + name)
            return Response({"file": web_paths})

# tiff version
# class InstanceProcessingView(APIView):
#     permission_classes = (permissions.IsAuthenticated, )

#     def get(self, request, format=None, **kwargs):
#         user = self.request.user
#         study_name = kwargs["dirName"]
#         instance_name = kwargs["instanceName"]
#         try:
#             study = Study.objects.get(name=study_name)
#         except IndexError:
#             return Response({"error": "study does not exist"})
#         try:
#             instance = Instance.objects.get(study=study, name=instance_name) # пока что для одного файла
#         except IndexError:
#             return Response({"error": "instance does not exist"})
#         web_path = settings.MEDIA_ROOT + "/" + user.username + "/" + study_name + "/" + "web" + "/"
#         path = settings.MEDIA_ROOT + "/" + user.username + "/" + study_name + "/" + instance.name
#         if os.path.isfile(path):
#             file_name = "".join(instance.name.split(".")[:-1]) + ".tiff"
#             if not os.path.isfile(web_path + file_name):
#                 if not os.path.exists(web_path):
#                     os.makedirs(web_path)
#                 try:
#                     tags = reformat_survey(path, web_path)
#                 except FileNotFoundError:
#                     return Response({"error": "file does not exist"})
#                 data = {
#                     "file": settings.HOST + settings.MEDIA_URL + user.username + "/" + study_name + "/" + "web" + "/" + file_name,
#                     "tags": tags,
#                     "success": "successfuly processed"
#                 }
#             else:
#                 try:
#                     with open(web_path + "".join(instance.name.split(".")[:-1]) + "_tags.json", "r") as f:
#                         tags = json.load(f)
#                 except FileNotFoundError:
#                     return Response({"error": "file does not exist"})
#                 data = {
#                     "file": settings.HOST + settings.MEDIA_URL + "/" + user.username + "/" + study_name + "/" + "web" + "/" + file_name,
#                     "tags": tags,
#                     "success": "successfuly processed"
#                 }
#             return Response(data)
#         else:
#             return Response({"error": "Слишком много файлов"})

# bytes version
# class InstanceProcessingView(APIView):
#     permission_classes = (permissions.IsAuthenticated, )

#     def get(self, request, format=None, **kwargs):
#         user = self.request.user
#         study_name = kwargs["dirName"]
#         instance_name = kwargs["instanceName"]
#         try:
#             study = Study.objects.get(name=study_name)
#         except IndexError:
#             return Response({"error": "Исследования не существует"})
#         try:
#             instance = Instance.objects.get(study=study, name=instance_name) # пока что для одного файла
#         except IndexError:
#             return Response({"error": "Объект исследования не найден"})
#         path = settings.MEDIA_ROOT + "/" + user.username + "/" + study_name + "/" + instance.name
#         if os.path.isfile(path):
#             file, tags = reformat_survey(path)
#             # data = {
#             #     "file": file,
#             #     "tags": tags,
#             # }
#             return HttpResponse(content=file, content_type='application/octet-stream')
#         else:
#              return Response({"error": "Слишком много файлов"})