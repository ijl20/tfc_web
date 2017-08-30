import json
import requests
from datetime import datetime, timedelta
from collections import namedtuple
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from csn.everynet_api import everynet_add_device, everynet_remove_device
from csn.forms import LWDeviceForm, LWApplicationForm, LWDeviceFormExtended
from csn.models import LOGGER, Destination, Sensor


@login_required
def devices(request):
    return render(request, 'csn/devices.html', {
        'devices': Sensor.get_all_lorawan_with_lwapps(user_id=request.user.id),
        'app_choices': Destination.get_all_everynet_jsonrpc(user_id=request.user.id)
    })


@login_required
def device(request, device_id):
    lwdevice = Sensor.get_lorawan(sensor_id=device_id, user_id=request.user.id)
    return render(request, 'csn/device.html', {
        'device': lwdevice,
    }) if lwdevice else HttpResponseNotFound()


@login_required
def new_device(request):
    lwdevice_form = LWDeviceForm(user=request.user)
    if request.method == "POST":
        lwdevice_form = LWDeviceFormExtended(request.POST, user=request.user)
        try:
            if lwdevice_form.is_valid():
                lwdevice = lwdevice_form.cleaned_data
                lwdevice_named = namedtuple("LWDevice", lwdevice.keys())(*lwdevice.values())
                if everynet_add_device(lwdevice_named):
                    Sensor.insert_lorawan(info=lwdevice)
                    return redirect('csn_devices')
                else:
                    lwdevice_form.add_error(field=None, error=lwdevice.error_message)
        except Exception as e:
            lwdevice_form.add_error(field=None, error=str(e))
        lwdevice_form.fields.pop('activation_type')
        lwdevice_form.fields.pop('nwkskey')
        lwdevice_form.fields.pop('appskey')
        lwdevice_form.fields.pop('dev_addr')
        lwdevice_form.fields.pop('app_key')
    return render(request, 'csn/new_device.html', {
        'form': lwdevice_form
    })


@login_required
def delete_device(request):
    if request.method == "POST":
        lwdevice = Sensor.get_lorawan(sensor_id=request.POST['sensor_id'], user_id=request.user.id)
        if not lwdevice:
            return HttpResponseNotFound()
        if everynet_remove_device(lwdevice):
            # TODO change this to Sensor.delete_lorawan?
            lwdevice.delete()
            messages.info(request, "Device deleted")
        else:
            messages.error(request, lwdevice.error_message)
    return redirect('csn_devices')


@login_required
def change_device_app(request):
    if request.method == "POST":
        lwdevice = Sensor.get_lorawan(sensor_id=request.POST['sensor_id'], user_id=request.user.id)
        lwapp = Destination.get_everynet_jsonrpc(destination_id=request.POST['app_id'], user_id=request.user.id)
        if not (lwapp and lwdevice):
            return HttpResponseNotFound()
        lwdevice.info['destination_id'] = lwapp.info['destination_id']
        lwdevice.info['destination_type'] = lwapp.info['destination_type']
        lwdevice.save()
    return redirect('csn_devices')


@login_required
def applications(request):
    return render(request, 'csn/applications.html', {
        'applications': Destination.get_all_everynet_jsonrpc(user_id=request.user.id)
    })


@login_required
def application(request, app_id):
    lwapp = Destination.get_everynet_jsonrpc_with_sensors(destination_id=app_id, user_id=request.user.id)
    return render(request, 'csn/application.html', {
        'application': lwapp,
    }) if lwapp else HttpResponseNotFound()


@login_required
def new_app(request):
    lwapplication_form = LWApplicationForm(user=request.user)
    if request.method == "POST":
        lwapplication_form = LWApplicationForm(request.POST, user=request.user)
        if lwapplication_form.is_valid():
            Destination.insert_everynet_jsonrpc(lwapplication_form.cleaned_data)
            return redirect('csn_applications')
    return render(request, 'csn/new_application.html', {
        'form': lwapplication_form,
    })


@login_required
def delete_app(request):
    if request.method == "POST":
        if not Destination.delete_everynet_jsonrpc(user_id=request.user.id, destination_id=request.POST['app_id']):
            return HttpResponseNotFound()
    return redirect('csn_applications')


def network_info(request):
    gateways = None
    error = False
    headers = \
        {
            'Authorization': settings.LW_API_KEY,
            'Content-Type': 'application/json'
        }
    response = requests.get(settings.EVERYNET_API_ENDPOINT + "gateways", headers=headers)
    if response.status_code != 200:
        LOGGER.error(response)
        error = True
    else:
        try:
            gateways = json.loads(response.content.decode('utf-8'))
        except Exception as e:
            LOGGER.error(e)
            error = True

    return render(request, 'csn/network_info.html', {
        'gateways': gateways['gateways'] if gateways and 'gateways' in gateways else None,
        'error': error,
    })


def gateway(request, gw_mac):
    error = False
    total_json = None
    headers = \
        {
            'Authorization': settings.LW_API_KEY,
            'Content-Type': 'application/json'
        }
    response_total = requests.get(settings.EVERYNET_API_ENDPOINT + "statistics/gateway/%s/total" % gw_mac,
                                  headers=headers)
    if response_total.status_code != 200:
        LOGGER.error(response_total)
        error = True
    else:
        try:
            total_json = json.loads(response_total.content.decode('utf-8'))
        except Exception as e:
            LOGGER.error(e)
            error = True
    response_graph = requests.get(
        settings.EVERYNET_API_ENDPOINT + "statistics/gateway/%s/graph?from_time=%s&to_time=%s&step=%s" %
        (gw_mac, int((datetime.utcnow() - timedelta(days=7)).timestamp()), int(datetime.utcnow().timestamp()), 1800),
        headers=headers)
    if response_graph.status_code != 200:
        LOGGER.error(response_graph)
        error = True

    return render(request, 'csn/gateway.html', {
        'total': total_json['total'] if total_json and 'total' in total_json else None,
        'graph': response_graph.content,
        'error': error,
        'gw_mac': gw_mac,
    })
