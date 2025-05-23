from django.db import models
from django.contrib.auth.models import User  # ✅ Import User model

class DroneLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="logs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    drone_model = models.CharField(max_length=100, default="Unknown")
    exhibit_no = models.CharField(max_length=100,default="N/A")

    def __str__(self):
        return self.file.name

class TelemetryLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="logs/telemetry/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    drone_model = models.CharField(max_length=100,default="Unknown")
    exhibit_no = models.CharField(max_length=100,default="N/A")

    def __str__(self):
        return self.file.name


class EXIFLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='exif_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Optional: exhibit_no, drone_model, etc.
