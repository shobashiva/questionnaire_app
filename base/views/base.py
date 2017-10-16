""" Views for the base application """
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.shortcuts import render, get_object_or_404, redirect
from base.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import requests
import json

from pcusa_po_app.forms import ForgotPasswordForm, ResetPasswordForm


def index(request):
    """ Default view for the root """
    return render(request, 'base/index.html', {})

def farewell(request):
    return render(request, 'base/farewell.html', {})

def forgot(request):
	if request.method == 'POST':
		form = ForgotPasswordForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data.get('email')
			r = requests.post('https://process-observations.ogapcusa.org/api/forgot', data={'email':email})
			if(r.status_code == 200):
				messages.add_message(request,messages.INFO,'Please check your email for a link to reset your password')
	else:
		form = ForgotPasswordForm()
	return render(request, 'base/forgot.html', {'form':form})

def reset(request):
	if request.method == 'POST':
		form = ResetPasswordForm(request.POST, token='')
		if form.is_valid():
			data = form.cleaned_data.get('newpassword')
			token = form.cleaned_data.get('token')
			r = requests.post('https://process-observations.ogapcusa.org/api/reset', data={'token':token,'newpassword':data})

			if(r.status_code == 400):
				messages.add_message(request,messages.INFO,'This reset password request has expired or already been used.')
			elif(r.status_code == 200):
				messages.add_message(request,messages.INFO,'Your password was reset, please log in')
				return redirect('login')


	else:
		token = request.GET.get('token')
		form = ResetPasswordForm(token=token)
	return render(request, 'base/forgot.html', {'form':form})

def health(request):
    return HttpResponse("<h1>Success</h1>")
    
@login_required
def profile(request):
	object = get_object_or_404(UserProfile, user=request.user)
	return render(request, 'base/profile.html', {'object':object})

