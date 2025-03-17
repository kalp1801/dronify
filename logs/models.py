from django.db import models

class DroneLog(models.Model):
    file = models.FileField(upload_to="logs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
