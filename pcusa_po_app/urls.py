""" Default urlconf for pcusa_po_app """

from emailusernames.forms import EmailAuthenticationForm, EmailUserCreationForm

from django.conf.urls import include, patterns, url
from django.contrib import admin
from .views import *
admin.autodiscover()


def bad(request):
    """ Simulates a server error """
    1 / 0

urlpatterns = patterns('',
    # Examples:
    url(r'^siteadmin/', include(admin.site.urls)),
    url(r'^bad/$', bad),
    url(r'', include('base.urls')), 
    #url(r'^(?P<id>\d+)/start/$', observation_start, name='observation_start'),
    
    url(r'beginobservation', beginobservation, name='beginobservation'), # select committee
    url(r'^(?P<id>\d+)/(?P<committee>\d+)/tally/$', tally_start, name='tally_start'), # tally participation
    url(r'^(?P<id>\d+)/questionnaire/$', questionnaire_start, name='questionnaire_start'), #questionnaire

    #url('^', include('django.contrib.auth.urls')), 
   
    #url(r'^forms/', include(forms_builder.forms.urls)),   
    url(r'^login$', 'django.contrib.auth.views.login', {'authentication_form': EmailAuthenticationForm}, name='login'),
    url(r'^register$', register,name='register'), 
    #url(r'^profile_edit$', register,name='register'),
    url(r'^accounts/login', 'django.contrib.auth.views.login', {'authentication_form': EmailAuthenticationForm}, name='login'),
    url(r'^accounts/profile', profile, name='profile'),
    url(r'^logout$', logout_view, name='logout'),

)