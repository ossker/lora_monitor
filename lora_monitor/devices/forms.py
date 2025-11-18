from django import forms
from .models import Device


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_id', 'dev_eui', 'name', 'description', 'is_active']