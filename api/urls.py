
from django.conf.urls import url, include, patterns
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from base import models
from api.views import auth

router = routers.DefaultRouter()
#router.register(r'iobs', IOBViewSet)

# IOB components
#router.register(r'rationale', RationaleViewSet)


urlpatterns = patterns(
    'api.views',
    url(r'^login', auth.login),
    url(r'^register', auth.register),
    url(r'^forgot', auth.forgot_password),
    url(r'^reset', auth.reset_password),
    url(r'^change_password', auth.change_password),
    url(r'^validate', auth.validate_reset_token),
#    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')), # browsable api
#    url(r'^iob/(?P<iob_id>[0-9]+)/details/?$', iob.detailView, name='iobdetails'), #this should only be used when displaying full details of an IOB, including it's components
) 

urlpatterns += router.urls