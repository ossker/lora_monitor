from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Device, SensorReading, NetworkMetadata
from .forms import DeviceForm
from django.utils import timezone
from geopy.geocoders import Nominatim
from django.db.models import Avg

def geocode_address(address):
    geolocator = Nominatim(user_agent="lora_monitor")
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None, None


def get_uplink_count(device_id):
    device = Device.objects.get(device_id=device_id)
    return NetworkMetadata.objects.filter(device=device).count()


def get_packet_loss(device_id):
    readings = SensorReading.objects.filter(device__device_id=device_id).order_by('timestamp')
    lost = 0
    prev_fcnt = None
    for r in readings:
        if r.f_cnt is not None:
            if prev_fcnt is not None:
                diff = r.f_cnt - prev_fcnt - 1
                if diff > 0:
                    lost += diff
            prev_fcnt = r.f_cnt
    return lost

@login_required
def device_list(request):
    devices = Device.objects.all()
    for device in devices:
        device.online = device.is_online()
    return render(request, 'devices/device_list.html', {'devices': devices})


@login_required
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    device_id = device.device_id
    device.online = device.is_online()
    readings = SensorReading.objects.filter(device=device).order_by('timestamp')
    timestamps = [r.timestamp.isoformat() for r in readings]
    temperatures = [r.temperature for r in readings]
    humidities = [r.humidity for r in readings]
    pressures = [r.pressure for r in readings]
    avg = get_device_avg_rssi_snr(device_id)
    heatmap = get_heatmap_data(device_id)
    restarts = detect_device_restarts(device_id)
    anomalies = detect_temperature_anomalies(device_id)
    packet_loss = get_packet_loss(device_id)
    uplink_count = get_uplink_count(device_id)
    return render(request, 'devices/device_detail.html', {
        'device': device,
        'readings': readings,
        'avg': avg,
        'heatmap': heatmap,
        'restarts': restarts,
        'anomalies': anomalies,
        'timestamps': timestamps,
        'temperatures': temperatures,
        'humidities': humidities,
        'pressures': pressures,
        'packet_loss': packet_loss,
        'uplink_count': uplink_count,
    })


@login_required
def device_create(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            if device.address:
                lat, lon = geocode_address(device.address)
                device.location_lat = lat
                device.location_lon = lon
            device.last_seen = timezone.now()
            device.save()
            return redirect('devices:list')
    else:
        form = DeviceForm()

    return render(request, 'devices/device_create.html', {'form': form})


@login_required
def device_update(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            device = form.save(commit=False)
            if device.address:
                lat, lon = geocode_address(device.address)
                device.location_lat = lat
                device.location_lon = lon
            device.save()
            return redirect('devices:detail', pk=device.pk)
    else:
        form = DeviceForm(instance=device)
    return render(request, 'devices/device_update.html', {'form': form, 'device': device})


@login_required
def device_delete(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        device.delete()
        return redirect('devices:list')
    return render(request, 'devices/device_confirm_delete.html', {'device': device})


def get_device_avg_rssi_snr(device_id):
    device = Device.objects.get(device_id=device_id)
    agg = NetworkMetadata.objects.filter(device=device).aggregate(
        avg_rssi=Avg('rssi'),
        avg_snr=Avg('snr')
    )
    return agg


def get_heatmap_data(device_id):
    from .models import NetworkMetadata, Device
    device = Device.objects.get(device_id=device_id)

    metadata = NetworkMetadata.objects.filter(device=device).exclude(
        gateway_lat__isnull=True,
        gateway_lon__isnull=True
    ).values('gateway_lat', 'gateway_lon', 'rssi')

    heatmap = [
        [m['gateway_lat'], m['gateway_lon'], abs(m['rssi'])]
        for m in metadata
    ]
    return heatmap

def detect_device_restarts(device_id):
    device = Device.objects.get(device_id=device_id)
    readings = SensorReading.objects.filter(device=device).order_by('timestamp')
    restarts = []

    prev_fcnt = None
    for r in readings:
        if r.f_cnt is not None:
            if prev_fcnt is not None and r.f_cnt < prev_fcnt:
                restarts.append({
                    'timestamp': r.timestamp,
                    'prev_fcnt': prev_fcnt,
                    'new_fcnt': r.f_cnt
                })
            prev_fcnt = r.f_cnt

    return restarts

def detect_temperature_anomalies(device_id, threshold=5.0):
    device = Device.objects.get(device_id=device_id)
    readings = SensorReading.objects.filter(device=device).order_by('timestamp')
    anomalies = []

    prev_temp = None
    for r in readings:
        temp = r.temperature
        if temp is not None and prev_temp is not None:
            if abs(temp - prev_temp) > threshold:
                anomalies.append({
                    'timestamp': r.timestamp,
                    'prev_temp': prev_temp,
                    'current_temp': temp
                })
        if temp is not None:
            prev_temp = temp

    return anomalies