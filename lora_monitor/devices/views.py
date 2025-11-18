from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Device, SensorReading
from .forms import DeviceForm

@login_required
def device_list(request):
    devices = Device.objects.all()
    return render(request, 'devices/device_list.html', {'devices': devices})


@login_required
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    readings = SensorReading.objects.filter(device=device).order_by('-timestamp')
    return render(request, 'devices/device_detail.html', {
        'device': device,
        'readings': readings
    })


@login_required
def device_create(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('devices:list')
    else:
        form = DeviceForm()

    return render(request, 'devices/device_create.html', {'form': form})


@login_required
def device_delete(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        device.delete()
        return redirect('devices:list')
    return render(request, 'devices/device_confirm_delete.html', {'device': device})
