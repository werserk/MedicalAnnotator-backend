from django.db import models
from django.conf import settings
import uuid

User = settings.AUTH_USER_MODEL

class AuthUploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.user.username
    
# функционал ctrl z под вопросом, непонятно, где и как хранить изображения