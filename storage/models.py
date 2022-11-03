from django.db import models
from django.utils.timezone import now
import uuid

from accounts.models import UserAccount


class Study(models.Model):
    HP = "HP"
    OT = "ОТ"
    BPR = "ВПР"
    P = "Р"

    STATE_COICES = [
        (HP, "Не размечен"),
        (OT, "Отклонён"),
        (BPR, "В процессе разметки "),
        (P, "Размечен"),
    ]
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, blank=True, null=True)
    date_upload = models.DateField(default=now, blank=True, null=True)
    done = models.CharField(max_length=10, blank=True, null=True)
    modality = models.CharField(max_length=16, null=True, blank=True)
    patient_id = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(choices=STATE_COICES, default='НР', max_length=3)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    def all(self):
        fields = self._meta.get_fields()
        values = {}
        for field in fields:
            values[field.attname] = getattr(self, field.attname)
        return values

    class Meta:
        ordering = ['date_upload']