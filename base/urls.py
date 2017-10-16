"""urlconf for the base application"""

from django.conf.urls import include, url, patterns
from django.contrib.auth import views as auth_views
# from base.views import (
#     ProcessObservationFormView
# )

urlpatterns = patterns('base.views.base',
    url(r'^api/', include('api.urls')),
    # url(r'^process-observation-form', base.views.forms.ProcessObservationFormView.as_view(), name='process_observation_form'),
    url(r'^(?:home)?$', 'index', name='index'),
    url(r'^farewell', 'farewell', name='farewell'),
    url(r'^forgot$', 'forgot', name='forgot'),
    url(r'^reset$', 'reset', name='reset'),
    url(r'^health/$', 'health', name='health'),

)
