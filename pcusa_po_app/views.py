from emailusernames.forms import EmailAuthenticationForm, EmailUserCreationForm

from django.shortcuts import render, get_object_or_404, redirect
from emailusernames.utils import create_user, get_user
#from django.contrib.auth import logout

from django.contrib.auth import login, logout
from django.db import IntegrityError

from datetime import datetime, date

#from base.views.forms import UserProfileForm
from base.models import UserProfile, Observation, Question, ObserverReport, Response, GridQuestionPrompt, GridQuestionResponse, CommitteeMember, Tally
from pcusa_po_app import helpers


from .forms import UserProfileForm, QuestionnaireForm, CommitteeForm, ObservationTimeForm, TallyForm
from django.forms.models import modelformset_factory
from django.forms.forms import NON_FIELD_ERRORS

from .helpers import get_committee_members_with_role, get_committee_members_with_role_from_tally, get_moderator_from_tally, get_vice_moderator_from_tally, get_sorted_tallys

import requests
import json

from django.contrib.auth.decorators import login_required


def register(request):
	if request.method == 'POST':
		form = EmailUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			profile = UserProfile.objects.get_or_create(user=user)
			return redirect('login')
		else:
			return render(request,'registration/register.html',{'form':form})
	else:
		form = EmailUserCreationForm()
		return render(request,'registration/register.html',{'form':form})

@login_required
def profile(request):
	if request.method == 'POST':
		edited_profile = get_object_or_404(UserProfile,user=request.user)
		form = UserProfileForm(request.POST,instance=edited_profile)
		if form.is_valid():
			profile = form.save()
			return redirect('index')
		else:	
			return render(request, 'registration/profile.html', {'form':form})
	else:
		user_profile = get_object_or_404(UserProfile,user=request.user)
		user_profile.email = request.user.email
		form = UserProfileForm(instance=user_profile)
		return render(request, 'registration/profile.html', {'form':form})

def logout_view(request):
	logout(request)
	return redirect('login')

# show and process choose committee form
def beginobservation(request):

	# getting committee data from the api
	r = requests.get('https://ogaevents.pcusa.org/register/api/committees/?ga=latest', headers={'X-API-KEY': 'd1832184-1899-4d8c-842e-e2822e0ef15f'})
	result = r.json()

	# building the list of tuples we will use in our form
	choice_list = []

	for committee in result:
		name = committee['name']
		number = committee['committee_number']
		option = '%s - %s' % (number, name,)
		choice_list.append((number,option,),)
		

	# sorting the list by the committee number
	choice_list.sort(key=lambda tup: tup[0])
	members = ''
	committeeMembers = ''
	membersByRole = ''

	# r = requests.get('https://ogaevents.pcusa.org/register/api/commissioners/?ga=latest&committee_number=10', headers={'X-API-KEY': 'd1832184-1899-4d8c-842e-e2822e0ef15f'})
	# test = r.json()
	form = CommitteeForm(choice_list)
	if request.method == 'POST':
		current_observation = Observation.objects.get(is_active=True)
		form = CommitteeForm(choice_list,request.POST)
		if form.is_valid():
			#Before we create the CommitteeTally, we need an ObserverReport to link it to
			# so we find the active Observation, and use that to create a new ObserverReport
			user_profile = get_object_or_404(UserProfile,user=request.user)
			committee_number = form.cleaned_data.get('committee_number')
			observer_report = ObserverReport.objects.create(observation=current_observation, user_profile=user_profile, committee_number=committee_number)
			observer_report.recorded_tally_start_date = datetime.now()
			observer_report.save()
			#get all the committee members and save them if they haven't already been created
			url = 'https://ogaevents.pcusa.org/register/api/commissioners/?ga=latest&committee_number=' + str(committee_number)
			r = requests.get(url, headers={'X-API-KEY': 'd1832184-1899-4d8c-842e-e2822e0ef15f'})
			members = r.json()
			committeeMembers = []

			for member in members:
				m_id = member['pk']
				first_name = member['first_name']
				last_name = member['last_name']
				badge_name = member['badge_name']
				presbytery = member['presbytery']
				gender = member['gender']
				race = member['race']
				age = member['age']
				role = member['role']
				secondary_role = member['secondary_role']
				has_special_needs = member['has_special_needs']
				needs_translation = member['needs_simultaneous_interpretation']

				if(badge_name):
					display_name = badge_name
				else:
					display_name = first_name

				try:
					commissioner = CommitteeMember.objects.get(commissioner_id=m_id)
					commissioner.first_name = first_name
					commissioner.last_name = last_name
					commissioner.badge_name = badge_name
					commissioner.presbytery = presbytery
					commissioner.gender = gender
					commissioner.race = race
					commissioner.age = age
					commissioner.role = role
					commissioner.secondary_role = secondary_role
					commissioner.has_special_needs = has_special_needs
					commissioner.needs_translation = needs_translation
					commissioner.display_name = display_name

				except CommitteeMember.DoesNotExist:
					commissioner= CommitteeMember(commissioner_id=m_id,first_name=first_name,display_name=display_name,badge_name=badge_name,last_name=last_name,presbytery=presbytery,gender=gender,race=race,age=age,role=role,secondary_role=secondary_role, has_special_needs=has_special_needs,needs_translation=needs_translation)
				
				commissioner.save()
				
				committeeMembers.append(commissioner)

				Tally.objects.create(member=commissioner,tally_report=observer_report)

			

			return redirect('tally_start', id=observer_report.pk,committee=committee_number)



	return render(request, 'observe/begin_observation.html',{'form':form})

# show and process tally form
def tally_start(request,id,committee):

	request_text = 'https://ogaevents.pcusa.org/register/api/committees/?ga=latest&committee_number=' + str(committee)
	r = requests.get(request_text, headers={'X-API-KEY': 'd1832184-1899-4d8c-842e-e2822e0ef15f'})
	result = r.json()
	committee_name = ''
	for c in result:
		committee_name = c['name']


	 #find the observer report we are viewing
	observer_report = get_object_or_404(ObserverReport, pk=id)
	commissioners = Tally.objects.filter(tally_report=observer_report)
	sorted_commissioners = get_sorted_tallys(commissioners)

	TallyFormSet = modelformset_factory(Tally,form=TallyForm, extra=0)
	formset = TallyFormSet(queryset=sorted_commissioners, prefix='REC')

	moderator = get_moderator_from_tally(commissioners)
	moderator_formset = TallyFormSet(queryset=moderator, prefix='MOD')

	vice_moderator = get_vice_moderator_from_tally(commissioners)
	vice_moderator_formset = TallyFormSet(queryset=vice_moderator, prefix='VICE')

	if request.method == 'POST':
		formset = TallyFormSet(request.POST, prefix='REC')
		moderator_formset = TallyFormSet(request.POST, prefix='MOD')
		vice_moderator_formset = TallyFormSet(request.POST, prefix='VICE')

		print(formset.errors)
		
		if formset.is_valid():
			formset.save()
			vice_moderator_formset.save()
			moderator_formset.save()
			observer_report.recorded_tally_observation_end_date = datetime.now()
			observer_report.save()

			return redirect('questionnaire_start', id=observer_report.pk)

	return render(request,'observe/tally_form.html', {'moderator_formset':moderator_formset,'vice_moderator_formset':vice_moderator_formset,'formset1':formset,'id':id, 'committee':committee, 'committee_name':committee_name})

#show and process questionnaire
def questionnaire_start(request, id):
	QuestionnaireFormSet = modelformset_factory(Response,form=QuestionnaireForm, extra=0)
	if request.method == 'POST':

		observer_report = get_object_or_404(ObserverReport, pk=id)
		observation_time_form = ObservationTimeForm(request.POST)
		if observation_time_form.is_valid():
			observer_report.observation_start_date = datetime.combine(date.today(), observation_time_form.cleaned_data.get('observation_start_date').time())
			observer_report.observation_end_date = datetime.combine(date.today(), observation_time_form.cleaned_data.get('observation_end_date').time())
			observer_report.save()			
		else:			
			pass #handle this error somehow?

		formset = QuestionnaireFormSet(request.POST)
		if formset.is_valid():
			for form in formset:
				print (form.cleaned_data)

				answer = form.cleaned_data.get('answer')

				# when a grid question is rendered on the form, it is rendered as just
				# a single questions.  When we save the form we need to save each prompt
				# as a new Response object
				if (answer == 'GQ'):
					r = form.save(commit=False)
					for index,prompt in enumerate(r.question.get_prompts()):
						prompt_name = 'gq_prompts_%s' % index
						prompt_response = 'gq_answers_%s' % index


						sub_prompt = form.cleaned_data.get(prompt_name)
						answer = form.cleaned_data.get(prompt_response)
						report = ObserverReport.objects.get(pk=id)
						answer_dict = {'answer':answer}

						# c = GridQuestionResponse.objects.create(question=r.question, prompt=GridQuestionPrompt.objects.get(pk=sub_prompt),answer=answer, observer_report=report)
						c = GridQuestionResponse.objects.update_or_create(question=r.question, prompt=GridQuestionPrompt.objects.get(pk=sub_prompt),observer_report=report, on_form=False, defaults=answer_dict)
						
				else:
					r = form.save(commit=False)
					r.answer = answer
					r.save()
					print(r.id)
			return redirect('farewell')

		else:
			print(formset)			
			return render(request, 'observe/questionnaire_form.html',{'observation_time_form':observation_time_form, 'formset':formset, 'id':id, 'general_form_error':'Please correct the errors below'})


	observer_report = get_object_or_404(ObserverReport, pk=id)
	response_set = observer_report.get_responses()
	
	formset = QuestionnaireFormSet(queryset=response_set)

	# Add Observation start and end time form
	observation_time_form = ObservationTimeForm(observer_report=observer_report)
	observation_time_form.instance = observer_report

	return render(request, 'observe/questionnaire_form.html',{'observation_time_form':observation_time_form, 'formset':formset, 'id':id})
