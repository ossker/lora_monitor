from django import forms
from .models import Device


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'device_id',
            'dev_eui',
            'dev_addr',
            'application_id',
            'address',
        ]