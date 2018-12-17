import logging
from django.core.cache import cache
from django.shortcuts import render
from django.conf import settings
from django.templatetags.static import static
import zeep
import zeep.transports
import zeep.cache
import re

logger = logging.getLogger(__name__)

# WSDL = 'https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2017-10-01'
WSDL = '/wsdl/OpenLDBWS_wsdl_2017-10-01.xml'

STATION_ABBREV = {
  'London Kings Cross': 'London Kings X',
  'London Liverpool Street': 'London Liv. St',
  'Birmingham New Street': "Birm'ham New St",
}


def station_board(request, ver=''):
    '''
    Retrieve a 'DepartureBoard' from National Rail Enquiries
    and render it as a web page
    '''
    station = request.GET.get('station', '')
    assert station, 'No station code found'
    offset = int(request.GET.get('offset', 0))

    cache_key = "station_board!{0}!{1}".format(station, offset)
    data = cache.get(cache_key)
    if data:
        logger.info('Cache hit for %s', cache_key)

    else:
        logger.info('Cache miss for %s', cache_key)
        data = {'messages': [], 'services': []}

        protocol = 'http://'
        if request.is_secure():
            protocol = 'https://'

        hostname = request.get_host()

        absolute_wsdl = protocol + hostname + WSDL

        try:
            transport = zeep.transports.Transport(cache=zeep.cache.SqliteCache())
            client = zeep.Client(wsdl=absolute_wsdl, transport=transport)
            raw_data = client.service.GetDepartureBoard(
                numRows=50, crs=station,
                _soapheaders={"AccessToken": settings.NRE_API_KEY},
                timeOffset=offset
            )
        except zeep.exceptions.XMLSyntaxError as e:
            logger.error("Error retrieving station board for '{0}'".format(station))
            logger.error("XMLSyntaxError: {0}".format(e))
            logger.error("content={0}".format(e.content))
            assert False, "Failed to retrieve station board"

        data['locationName'] = raw_data['locationName']
        data['generatedAt'] = raw_data['generatedAt'].strftime("%H:%M")

        if raw_data['nrccMessages']:
            for message in raw_data['nrccMessages']['message']:
                for key in message:
                    data['messages'].append(re.sub('<[^<]+?>', '', message[key]))
        if len(data['messages']) > 1:
            data['messages'] = ['Multiple travel alerts in force - see www.nationalrail.co.uk for details.']

        if raw_data['trainServices']:
            for service in raw_data['trainServices']['service']:
                this_service = {}
                this_service['std'] = service['std']
                this_service['etd'] = service['etd']
                dest = service['destination']['location'][0]['locationName']
                if dest in STATION_ABBREV:
                    dest = STATION_ABBREV[dest]
                this_service['destination'] = dest
                data['services'].append(this_service)

        cache.set(cache_key, data, timeout=30)

    template = 'smartpanel/station_board{0}.html'.format(ver)
    return render(request, template, {'data': data})
