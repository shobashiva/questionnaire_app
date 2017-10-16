from django import forms

from base.models import Observation, Question, UserProfile, FreeResponseQuestion, SingleAnswerQuestion, MultipleChoiceQuestion, GridQuestion, Response, GridQuestionPrompt, Tally, ObserverReport

import pytz
from datetime import date, datetime, timedelta
from django.utils import timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Fieldset, Div, HTML, MultiField
from crispy_forms.bootstrap import FormActions, InlineRadios, PrependedText, PrependedAppendedText


class UserProfileForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = 'profile'
			# self.helper.form_class = 'form-horizontal'
		# self.helper.label_class = 'col-md-2'
		# self.helper.field_class = 'col-md-8'
		self.helper.add_input(Submit('submit', 'Submit'))
		super(UserProfileForm,self).__init__(*args,**kwargs)
		self.helper.layout = Layout(
			Field('email', readonly=True),
			Div(
				'first_name',
				'last_name',
			),
			Div(
				'age',
				css_class='profile-age'
			),
			Div(
				'gender',
				'race'
			)
		)
		

	class Meta:
		model = UserProfile
		fields = ('first_name','last_name','email','age','gender','race',)


class CommitteeForm(forms.ModelForm):
	def __init__(self, choice_list, *args, **kwargs):
		self.helper = FormHelper()


		self.helper.form_action = 'beginobservation'
		self.helper.add_input(Submit('submit', 'Continue'))
		super(CommitteeForm,self).__init__(*args,**kwargs)
		
		self.fields['committee_number'] = forms.ChoiceField()
		self.fields['committee_number'].choices = choice_list
		self.fields['committee_number'].label = 'Which committee are you observing?'

		self.helper.layout = Layout(
			Field('committee_number'),
		)

	class Meta:
		model = ObserverReport
		fields = ('committee_number',)


class TallyForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		
		instance = kwargs['instance']

		super(TallyForm,self).__init__(*args,**kwargs)

		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_tag = False

		#self.fields['count'].label = '%s %s' % (instance.member.first_name, instance.member.last_name)
		self.fields['count'].label = ''
		self.fields['count'].widget.attrs['readonly'] = True

		#name_string = instance.member.first_name + ' ' + instance.member.last_name
		last_initials = instance.member.last_name[:1]
		first_name = instance.member.display_name


		name_string = first_name + " " + last_initials		
		self.fields['name'] = forms.CharField(initial=name_string, required=False)
		self.fields['name'].widget.attrs['readonly'] = True
		self.fields['name'].label = ''

		self.fields['presbytery'] = forms.CharField(initial=instance.member.presbytery, required=False)
		self.fields['presbytery'].label = ''
		self.fields['presbytery'].widget.attrs['readonly'] = True

		role = instance.member.identities_indicator()
		self.fields['role'] = forms.CharField(initial=role, required=False)
		self.fields['role'].label = ''
		self.fields['role'].widget.attrs['readonly'] = True


		# self.helper.form_class = 'form-inline'
		# self.helper.field_template = 'bootstrap3/layout/inline_field.html'
		# self.helper.label_class = 'add_td_label'
		# self.helper.field_class = 'add_td'
		if (instance.member.secondary_role):
			role_string = 'Mod'
			print(instance.member.secondary_role)
			if (instance.member.secondary_role == 'Committee Vice Moderator'):
				role_string = 'V. Mod'

			self.fields['role'] = forms.CharField(initial=role_string)
			self.fields['role'].label = ''
			self.fields['role'].widget.attrs['readonly'] = True

			self.helper.layout = Layout(
				Div(
					Div('role', css_class='tally-role add_td'),
					Div('name', css_class='tally-row add_td tally-name'),
					Div('presbytery', css_class='tally-row add_td'),
					Div(PrependedAppendedText('count','<span class="dec">-</span>','<span class="inc">+</span>'), css_class='tally-count add_td'),
				css_class='add_tr'),
			)
		else:

			self.helper.layout = Layout(
				Div(
					Div('name', css_class='tally-row add_td tally-name'),
					Div('presbytery', css_class='tally-row add_td'),
					Div('role', css_class='add_td tally-age'),
					Div(PrependedAppendedText('count','<span class="dec">-</span>','<span class="inc">+</span>'), css_class='tally-count add_td'),
				css_class='add_tr'),
			)



	class Meta:
		model = Tally
		fields = ('count',)

class ForgotPasswordForm(forms.Form):
	def __init__(self,*args,**kwargs):
		super(ForgotPasswordForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = 'forgot'
		self.helper.add_input(Submit('submit', 'Submit'))

		self.fields['email'] = forms.EmailField()
		self.fields['email'].label = 'Please enter your registered email address. You will be emailed a link to reset your password.'

		self.helper.layout = Layout(
			Div('email', css_class='farewell'),
		)

class ResetPasswordForm(forms.Form):
	def __init__(self,*args,**kwargs):
		self.token = kwargs.pop('token')
		super(ResetPasswordForm, self).__init__(*args,**kwargs)

		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = 'reset'
		self.helper.add_input(Submit('submit','Submit'))

		self.fields['token'] = forms.CharField(initial=self.token)
		self.fields['token'].widget = forms.HiddenInput()

		self.fields['newpassword'] = forms.CharField()
		self.fields['newpassword'].widget = forms.PasswordInput()
		self.fields['newpassword'].label = 'Enter your new password'


		self.fields['newpassword2'] = forms.CharField()
		self.fields['newpassword2'].widget = forms.PasswordInput()
		self.fields['newpassword2'].label = 'Re-enter your new password'

		self.helper.layout = Layout(
			Div('token', css_class='farewell'),
			Div('newpassword', css_class='farewell'),
			Div('newpassword2', css_class='farewell')
		)


	def clean(self):
		cleaned_data = super(ResetPasswordForm, self).clean()
		data = cleaned_data.get("newpassword")
		data2 = cleaned_data.get("newpassword2")

		if (data == data2):
			pass
		else:
			raise forms.ValidationError("You did not re-enter your password correctly")

		# return cleaned_data

class ObservationTimeForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		
		observer_report = None
		if 'observer_report' in kwargs:
			observer_report = kwargs.pop('observer_report')

		super(ObservationTimeForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_tag = False

		#self.fields['observation_start_date'] = forms.DateTimeField(input_formats=['%m/%d/%Y %I:%M %p'],)
		self.fields['observation_start_date'] = forms.DateTimeField(input_formats=['%I:%M %p'],)
		self.fields['observation_start_date'].label = 'When did you start observing?'
		self.fields['observation_start_date'].widget = forms.TextInput(attrs={'class':'datetimepicker'})

		#self.fields['observation_end_date'] = forms.DateTimeField(input_formats=['%m/%d/%Y %I:%M %p'],)
		self.fields['observation_end_date'] = forms.DateTimeField(input_formats=['%I:%M %p'],)
		self.fields['observation_end_date'].label = 'When did you finish observing?'
		self.fields['observation_end_date'].widget = forms.TextInput(attrs={'class':'datetimepicker form-control'})

		if observer_report is not None:
			tz_creation_date = observer_report.created_date.astimezone(timezone.get_current_timezone())
			print (tz_creation_date)
			#self.fields['observation_start_date'].initial=tz_creation_date.strftime('%m/%d/%Y %I:%M %p')
			self.fields['observation_start_date'].initial=(tz_creation_date + timedelta(hours=-1)).strftime('%I:%M %p')
			#self.fields['observation_end_date'].initial=(tz_creation_date + timedelta(hours=1)).strftime('%m/%d/%Y %I:%M %p')
			self.fields['observation_end_date'].initial=(tz_creation_date).strftime('%I:%M %p')

		self.helper.layout = Layout(
			Field('observation_start_date'),
			Field('observation_end_date'),
		)

	class Meta:
		model = ObserverReport
		fields = ('observation_start_date', 'observation_end_date',)

class QuestionnaireForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		

		#we need to render different layouts for different questions
		instance = kwargs['instance']

		if(instance.on_form == False):
			pass

		question = instance.question

		#Decide the question type - either FRQ, SAQ, MCQ
		question_type = 'FRQ'
		if (isinstance(question,FreeResponseQuestion)):
			pass
		elif (isinstance(question,SingleAnswerQuestion)):
			question_type = 'SAQ'
		elif (isinstance(question,MultipleChoiceQuestion)):
			question_type = 'MCQ'
		elif (isinstance(question,GridQuestion)):
			question_type = 'GQ'


		super(QuestionnaireForm,self).__init__(*args,**kwargs)

		#begin helper setup
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_tag = False
		

        #if FRQ show the question field
		if (question_type == 'FRQ'):
			self.fields['answer'] = forms.CharField(widget=forms.Textarea, required=False)

		if (question_type == 'SAQ'):
			print(question.get_options())
			self.fields['answer'] = forms.ModelChoiceField(queryset=question.get_options())

		if (question_type == 'MCQ'):
			self.fields['answer'] = forms.ModelMultipleChoiceField(queryset=question.get_options())
			self.fields['answer'].widget = forms.CheckboxSelectMultiple()

		if (question_type == 'GQ'):
			self.fields['answer'] = forms.CharField()

	    #question_prompt = '%d %s' % (instance.sort_order, instance.prompt)

		# self.fields['question'] = question
		self.fields['question'].label = ''
		self.fields['question'].widget = forms.HiddenInput()

		# self.helper.form_class = 'form-horizontal'
		# self.helper.label_class = 'col-md-2'
		# self.helper.field_class = 'col-md-8'
		#self.helper.add_input(Submit('submit','Submit'))


		if (question_type == 'FRQ'):

			#self.fields['answer'].label = '%d. %s' % (question.sort_order, question.prompt)
			self.fields['answer'].label = '%s' % (question.prompt)
			self.helper.layout = Layout(
				'answer',
			)

		if (question_type == 'SAQ'):

			self.fields['answer'].label = '%s' % (question.prompt)
			self.helper.layout = Layout(
				'answer'
			)

		if (question_type == 'MCQ'):

			self.fields['answer'].label = '%s' % (question.prompt)
			self.helper.layout = Layout(
				'answer'
			)

		if (question_type == 'GQ'):
			main_prompt = '%s' % (question.prompt)
			self.fields['answer'].label = '%d. %s' % (question.sort_order, question.prompt)

			self.helper.layout = Layout(
				Fieldset(
					main_prompt,
					Div('answer')
				),
				# HTML("<div class='add_tr'><div class='add_td_label'></div><div class='add_td'>Most and </div></div>")
				
			)

			#dynamically building the grid questions prompt
			#by prompt
			sub_prompt = question.get_prompts()
			options = question.get_options()
			self.helper.label_class = 'add_td_label col-lg-2'
			self.helper.field_class = 'add_td'
			self.fields['answer'].widget = forms.HiddenInput(attrs={'value':'GQ'})
			for index,prompt in enumerate(sub_prompt):
				name = 'gq_answers_%s' % index
				name2 = 'gq_prompts_%s' % index
				self.fields[name2] = forms.CharField()
				self.fields[name2].widget = forms.HiddenInput(attrs={'value':prompt.id})
				self.fields[name] = forms.ModelChoiceField(queryset=options)
				self.fields[name].label = prompt.sub_prompt
				self.helper.layout.extend([Div(name2)])
				self.helper.layout.extend([
					Div(
						name,
						css_class='add_tr'
					)
				])



	class Meta:
		model = Response
		fields = ('question',)


