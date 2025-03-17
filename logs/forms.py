from django import forms
from .models import DroneLog

class DroneLogForm(forms.ModelForm):
    class Meta:
        model = DroneLog
        fields = ['file']
