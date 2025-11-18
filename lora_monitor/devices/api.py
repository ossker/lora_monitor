from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .models import Device, SensorReading
from .schemas import TTNWebhook
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_reading_to_ws(reading):
    channel_layer = get_channel_layer()
    group_name = f'device_{reading.device.device_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'device_update',
            'data': {
                'temperature': reading.temperature,
                'humidity': reading.humidity,
                'pressure': reading.pressure,
                'timestamp': reading.timestamp.isoformat(),
            }
        }
    )


class TTNWebhookView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            validated = TTNWebhook.model_validate(request.data)
        except Exception as e:
            return Response({"error": f"Pydantic validation error: {e}"}, status=400)

        dev = validated.data.end_device_ids
        device_id = dev.device_id
        dev_eui = dev.dev_eui

        device = Device.objects.filter(device_id=device_id, dev_eui=dev_eui).first()
        if not device:
            return Response({"error": f"Device {device_id} not registered"}, status=404)

        uplink = validated.data.uplink_message

        decoded = uplink.decoded_payload or {}
        temperature = decoded.get("temperature_1")
        humidity = decoded.get("relative_humidity_2")
        pressure = decoded.get("barometric_pressure_3")

        reading = SensorReading.objects.create(
            device=device,
            temperature=temperature,
            humidity=humidity,
            pressure=pressure,
        )
        send_reading_to_ws(reading)
        device.last_seen = timezone.now()
        device.save()

        return Response({"status": "ok"}, status=200)
