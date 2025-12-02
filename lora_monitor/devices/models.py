from django.db import models
from django.utils import timezone


class Device(models.Model):
    device_id = models.CharField(max_length=128, unique=True)
    dev_eui = models.CharField(max_length=32, db_index=True)
    dev_addr = models.CharField(max_length=32, blank=True, null=True)
    application_id = models.CharField(max_length=128)

    address = models.CharField(max_length=255, blank=True, null=True)
    location_description = models.CharField(max_length=255, blank=True, null=True)
    location_lat = models.FloatField(blank=True, null=True)
    location_lon = models.FloatField(blank=True, null=True)

    last_seen = models.DateTimeField(blank=True, null=True)
    last_rssi = models.FloatField(blank=True, null=True)
    last_snr = models.FloatField(blank=True, null=True)
    last_gateway_id = models.CharField(max_length=128, blank=True, null=True)

    last_fcnt = models.IntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_online(self, timeout_minutes=30):
        if not self.last_seen:
            return False
        return (timezone.now() - self.last_seen).total_seconds() < timeout_minutes * 60

    def __str__(self):
        return f"{self.device_id} ({self.dev_eui})"


class SensorReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="readings")
    timestamp = models.DateTimeField(auto_now_add=True)

    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    f_cnt = models.IntegerField(blank=True, null=True)
    raw_payload = models.TextField(blank=True, null=True)
    decoded_payload_json = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Reading {self.id} @ {self.timestamp} for {self.device.device_id}"


class NetworkMetadata(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="network_meta")
    timestamp = models.DateTimeField(default=timezone.now)

    gateway_id = models.CharField(max_length=128)
    rssi = models.FloatField()
    snr = models.FloatField()
    channel_index = models.IntegerField(blank=True, null=True)

    gateway_lat = models.FloatField(blank=True, null=True)
    gateway_lon = models.FloatField(blank=True, null=True)
    gateway_alt = models.FloatField(blank=True, null=True)

    uplink_token = models.TextField(blank=True, null=True)
    received_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Meta {self.gateway_id} ({self.rssi} dBm)"