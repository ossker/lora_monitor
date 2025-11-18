from django.db import models

class Device(models.Model):
    device_id = models.CharField(
        max_length=64,
        unique=True,
        help_text="ID urządzenia z TTN (np. fake5)"
    )
    dev_eui = models.CharField(
        max_length=32,
        unique=True,
        help_text="DevEUI urządzenia z TTN"
    )
    name = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Opcjonalna nazwa urządzenia"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Opis  urządzenia"
    )
    last_seen = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Data ostatniego odebrania pakietu z TTN"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Czy urządzenie jest aktywne"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.device_id


class SensorReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="readings")
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.device_id} @ {self.timestamp}"