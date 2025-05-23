from django import forms
from .models import DroneLog, TelemetryLog
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class DroneLogForm(forms.ModelForm):
    class Meta:
        model = DroneLog
        fields = ['file', 'drone_model', 'exhibit_no']

class TelemetryUploadForm(forms.ModelForm):
    class Meta:
        model = TelemetryLog
        fields = ['file', 'drone_model', 'exhibit_no']

# EXIF doesn’t use a model, so you’ll need a plain form:
class EXIFUploadForm(forms.Form):
    image = forms.ImageField()
    drone_model = forms.CharField(max_length=100)
    exhibit_no = forms.CharField(max_length=100)

    
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2")
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }