from django.views.generic import TemplateView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, render, redirect

from base.models import UserProfile
from django import forms

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('first_name','last_name','email','age','gender','race',)

class ProcessObservationFormView(TemplateView):
    '''ProcessObservationForm'''
    template_name = 'base/process-observation-form.html'

    def get(self, request, *args, **kwargs):
        #token = Token.objects.get_or_create(user=request.user)[0]

        return render(request, self.template_name, {'test': 'test'})

    def dispatch(self, request, *args, **kwargs):
       return super(self.__class__, self).dispatch(request, *args, **kwargs)