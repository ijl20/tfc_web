import codecs
import requests
import json
from urllib.request import urlopen
from django.http import JsonResponse
from django.shortcuts import render


def index(request):
    return render(request, 'parking/home.html', {})

def parking_plot(request, parking_id):
    reader = codecs.getreader("utf-8")
    parking_json = json.load(reader(urlopen(
        'http://tfc-app2.cl.cam.ac.uk//api/dataserver/parking/occupancy/cam_park_local/grand-arcade-car-park/2016/11/11'
        # 'http://smartcambridge.org/api/dataserver/zone/config/%s' % zone_id
    )))
    #parking['name'] = 'Name of the Parking Area='+parking_id

    api_parking_occupancy = 'http://tfc-app2.cl.cam.ac.uk/api/dataserver/parking/occupancy/cam_park_local/grand-arcade-car-park/2016/11/11'
    
    return render(request, 'parking/parking_plot.html', {
        'config_parking_id': parking_id,
        'config_yyyy' : 2016, #debug
        'config_MM':    11,   #debug
        'config_dd':    11,   #debug
        'config_parking_data': json.dumps(parking_json),
        'api_parking_occupancy': api_parking_occupancy
    })

