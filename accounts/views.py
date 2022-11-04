from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from accounts.serializers import UsersListViewSerializer
from .models import UserAccount, User

class SignupView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = self.request.data

        username = data["username"]
        password = data["password"]
        password2 = data["password2"]
        if "is_superuser" in data:
            is_superuser = data["is_superuser"]
        else:
            is_superuser = False

        if password == password2:
            if UserAccount.objects.filter(username=username).exists():
                return Response({"error": "Username already exists"})
            else:
                if len(password) < 6:
                    return Response({"error": "Password must be at least 6 characters"})
                else:
                    if is_superuser:
                        UserAccount.objects.create_advanced_user(password=password, username=username)
                        return Response({"success": "User created successfully"})
                    else:
                        UserAccount.objects.create_common_user(password=password, username=username)
                        return Response({"success": "User created successfully"})
        else:
            return Response({"error": "Passwords do not match"})


class UsersListView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = UsersListViewSerializer
    
    def get(self, request, format=None):
        try:
            user = request.user.superuser
        except UserAccount.superuser.RelatedObjectDoesNotExist:
            raise Http404
        users = user.users.all()
        data = []
        for related in users:
            related_user = related.related_user

            data.append(
                {"username": related_user.username,
                "studies_completed": related_user.studies_completed,
                "studies": related_user.study_set.all().count(),
                "unique_id": related_user.unique_id
                }
            )
        return Response(data)


class UsersManyToManyView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None, **kwargs):
        try:
            user = request.user.superuser
        except UserAccount.superuser.RelatedObjectDoesNotExist:
            return Response({"error": "Вы не можете получить доступ к этому аккаунту"})
        try:
            user_refer = UserAccount.objects.get(unique_id=kwargs['refer']).user
        except Exception:
            return Response({"error": "Аккаунта, по ссылке которого вы перешли, не существует"})

        if user == user_refer:
             return Response({"error": "У вас уже есть доступ к этому аккаунту"})
        elif type(user_refer) == type(User()):
            try:
                user.users.add(user_refer)
                user.save()
            except Exception:
                return Response({"error": "У вас уже есть доступ к этому аккаунту"})
        else:
            return Response({"error": "Вы не можете получить доступ к этому аккаунту"})
        return Response({"success": f"Доступ к исследованиям аккаунта получен"})


class UniqueIDView(APIView):
    def get(self, request, format=None):
        user = request.user
        return Response({"unique_id": user.unique_id})
        


        