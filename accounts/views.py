from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status


class CurrentUser(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None):
        user = self.request.user
        if not user.username:
            return Response({"error": "Войдите пожалалуйста в аккаунт"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"user": {"name": user.username}}, status=status.HTTP_200_OK)
