from typing import Optional
import base64
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.utils import timezone

from .models import Device, SensorReading, NetworkMetadata
from .schemas import TTNWebhook
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

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


def decode_payload(base64_payload: str) -> Optional[dict]:
    try:
        data = base64.b64decode(base64_payload)
    except Exception:
        return None

    if len(data) < 6:
        return None

    temperature_raw = int.from_bytes(data[0:2], "big", signed=True)
    humidity_raw = int.from_bytes(data[2:4], "big")
    pressure_raw = int.from_bytes(data[4:6], "big")

    return {
        "temperature": temperature_raw / 10.0,
        "humidity": humidity_raw / 10.0,
        "pressure": pressure_raw / 10.0,
        "raw_hex": data.hex(),
    }

class TTNWebhookView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            validated = TTNWebhook.model_validate(request.data)
        except Exception as e:
            logger.error(f"Pydantic validation error: {e}")
            return Response({"status": "ignored"}, status=200)

        dev = validated.data.end_device_ids
        device_id = dev.device_id
        dev_eui = dev.dev_eui
        dev_addr = dev.dev_addr
        application_id = dev.application_ids.application_id

        device = Device.objects.filter(device_id=device_id, dev_eui=dev_eui).first()
        if not device:
            logger.warning(f"Received TTN uplink for unknown device {device_id}/{dev_eui}")
            return Response({"status": "ok"}, status=200)

        uplink = validated.data.uplink_message

        for meta in uplink.rx_metadata:
            NetworkMetadata.objects.create(
                device=device,
                gateway_id=meta.gateway_ids.gateway_id,
                rssi=meta.rssi,
                snr=meta.snr,
                channel_index=meta.channel_index,
                uplink_token=meta.uplink_token,
                received_at=meta.received_at,
                gateway_lat=meta.location.latitude if meta.location else None,
                gateway_lon=meta.location.longitude if meta.location else None,
                gateway_alt=meta.location.altitude if meta.location else None,
            )

            device.last_rssi = meta.rssi
            device.last_snr = meta.snr
            device.last_gateway_id = meta.gateway_ids.gateway_id

        raw_payload = uplink.frm_payload
        if uplink.decoded_payload:
            decoded_payload = uplink.decoded_payload
            temperature = decoded_payload.temperature_1
            humidity = decoded_payload.relative_humidity_2
            pressure = decoded_payload.barometric_pressure_3
        else:
            manually_decoded_payload = decode_payload(raw_payload)
            temperature = manually_decoded_payload.get("temperature")
            humidity = manually_decoded_payload.get("humidity")
            pressure = manually_decoded_payload.get("pressure")
            decoded_payload = manually_decoded_payload

        f_cnt = uplink.f_cnt
        reading = SensorReading.objects.create(
            device=device,
            temperature=temperature,
            humidity=humidity,
            pressure=pressure,
            raw_payload=raw_payload,
            decoded_payload_json=decoded_payload,
            f_cnt=f_cnt
        )

        device.last_seen = timezone.now()
        device.last_fcnt = uplink.f_cnt
        device.save(update_fields=["dev_eui", "dev_addr", "application_id",
                                   "last_seen", "last_fcnt",
                                   "last_rssi", "last_snr", "last_gateway_id"])

        send_reading_to_ws(reading)

        return Response({"status": "ok"}, status=200)
