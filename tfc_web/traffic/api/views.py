from datetime import timedelta
import logging

from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.schemas import AutoSchema

from api.auth import default_authentication, default_permission, default_throttle
from transport.api.views import Pagination
from .serializers import (
    ZoneListSerializer, ZoneConfigSerializer, ZoneHistorySerializer, ANPRCameraSerializer)
from api import util, auth, api_docs

import coreapi
import coreschema

from ..models import ANPRCamera

logger = logging.getLogger(__name__)


def get_zone_config(zone_id=None):
    if zone_id is None:
        return util.get_config('zone')
    else:
        try:
            return util.get_config('zone', zone_id,
                                   'zone_list', 'zone.id')
        except (util.TFCValidationError) as e:
            raise NotFound("Zone not found: {0}".format(e))


def swap_dot_and_underscore(data):
    ''' serializer can't cope with '.' in keys - switch to '_' '''
    return {key.replace('.', '_'): value for (key, value) in data.items()}


class ZoneList(auth.AuthenticateddAPIView):
    '''
    List metadata for all known zones, including each zone's
    _zone_id_.
    '''
    def get(self, request):
        data = get_zone_config()
        # serializer can't cope with '.' in keys - switch to '_'
        fixed_zones = []
        for zone in data['zone_list']:
            fixed_zone = swap_dot_and_underscore(zone)
            fixed_zones.append(fixed_zone)
        serializer = ZoneListSerializer({"zone_list": fixed_zones})
        return Response(serializer.data)


class ZoneConfig(auth.AuthenticateddAPIView):
    '''
    Return the metadata for a single zone identified by _zone_id_.
    '''
    schema = AutoSchema(manual_fields=api_docs.zone_id_fields)

    def get(self, request, zone_id):
        data = get_zone_config(zone_id)
        serializer = ZoneConfigSerializer(swap_dot_and_underscore(data))
        return Response(serializer.data)


class ZoneHistory(auth.AuthenticateddAPIView):
    '''
    Return historic zone data for the single zone identified by _zone_id_.
    Data is returned in 24-hour chunks from _start_date_ to _end_date_
    inclusive. A most 31 day's data can be retrieved in a single request.
    '''
    schema = AutoSchema(manual_fields=api_docs.zone_id_fields+api_docs.list_args_fields)

    def get(self, request, zone_id):

        args = util.ListArgsSerializer(data=request.query_params)
        args.is_valid(raise_exception=True)

        # Note that this validates zone_id!
        get_zone_config(zone_id)

        start_date = args.validated_data.get('start_date')
        end_date = args.validated_data.get('end_date')
        if end_date is None:
            end_date = start_date
        day_count = (end_date - start_date).days + 1

        results = []
        for date in (start_date + timedelta(n) for n in range(day_count)):
            try:
                filename = (
                    'cloudamber/sirivm/data_zone/'
                    '{1:%Y}/{1:%m}/{1:%d}/{0}_{1:%Y-%m-%d}.txt'
                    .format(zone_id, date)
                    )
                results = results + util.read_json_fragments(filename)
            except (FileNotFoundError):
                pass
        serializer = ZoneHistorySerializer({'request_data': results})
        return Response(serializer.data)


class ANPRCameraList(generics.ListAPIView):
    """
    Return a list of bus stops.
    """
    queryset = ANPRCamera.objects.all()
    serializer_class = ANPRCameraSerializer

    authentication_classes = default_authentication
    permission_classes = default_permission
    throttle_classes = default_throttle
