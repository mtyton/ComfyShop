from django.db import models
from django.core.files.storage import Storage


class DocumentTemplate(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="doc_templates/", )

    def __str__(self) -> str:
        return self.name
