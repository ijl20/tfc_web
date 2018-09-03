from django.conf.urls import include
from django.conf.urls import url
from django.views.generic import TemplateView

from rest_framework.documentation import include_docs_urls

from .api_docs import api_description


# These are the URL patterns for which documentation should
# be generated
docpatterns = [
    url(r'^/api/v1/parking/', include('parking.api.urls')),
    url(r'^/api/v1/zone/', include('traffic.api.urls')),
    url(r'^/api/v1/aq/', include('aq.api.urls')),
    # Import transport views previously served under /transport/api/
    url(r'^/api/v1/transport/', include('transport.api.urls')),
]

# These are all the URLs
urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="api/index.html")),
    # url(r'', include('authmultitoken.endpoint_urls')),
    url(r'', include('authmultitoken.html_urls')),
    url(r'^auth/', include('api.auth_urls')),
    url(r'^docs/', include_docs_urls(
        title='SmartCambridge API',
        description=api_description,
        patterns=docpatterns))
    ] + docpatterns
