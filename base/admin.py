from django.contrib import admin
from .models import UserProfile,Observation, Question, FreeResponseQuestion, SingleAnswerQuestion, SingleAnswerOption
from .models import MultipleChoiceQuestion, MultipleChoiceOption, GridQuestionOption, GridQuestion, GridQuestionPrompt,ObserverReport, SingleAnswerResponse, FreeResponseAnswer, ObserverReport, GridQuestionResponse, MultipleChoiceResponse
from .models import CommitteeMember, Tally
from adminsortable2.admin import SortableInlineAdminMixin
from adminsortable2.admin import SortableAdminMixin
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.util import quote

from django.conf.urls import include, patterns, url

import csv
from django import http
from django.http import HttpResponse
from django.utils.encoding import smart_str

def pull_all_tallys(modeladmin,request,queryset):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="observation_tally_export.csv"'

	writer = csv.writer(response, csv.excel)	

	for observation in queryset:
		
		writer.writerow([
			observation,
		])	

		committee_list = ObserverReport.objects.all().order_by().values_list('committee_number', flat=True).distinct().order_by('committee_number')
		for com in committee_list:
			
			tallys = Tally.objects.filter(tally_report__committee_number=com).order_by('member__last_name', 'member__first_name')

			if tallys is not None:
				writer.writerow([
					'Committee Number', 
					'Member Last Name',
					'Member First Name',
					'Gender',
					'Race',
					'Age',
					'Role',
					'Observation Date',
					'Tally',
				])
				for tally in tallys:
					observation = tally.tally_report.observation
					if observation in queryset:
						writer.writerow([
						smart_str(tally.tally_report.committee_number),
						smart_str(tally.member.last_name),
						smart_str(tally.member.first_name),
						smart_str(tally.member.gender),
						smart_str(tally.member.race),
						smart_str(tally.member.age),
						smart_str(tally.member.role),
						smart_str(tally.tally_report.observation_start_date),
						smart_str(tally.count),
	        		])

				writer.writerow([''])

	return response



def pull_all_responses(modeladmin,request,queryset):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="observation_response_export.csv"'

	writer = csv.writer(response, csv.excel)	

	for observation in queryset:
		
		writer.writerow([
			observation,
		])	

		#get all questions in observation
		questions = Question.objects.filter(observation=observation)

		for question in questions:

			writer.writerow([
				question,
			])

			#determine the type of question to determine the display of the response
			question_type = question.question_type()

			#free response questions
			if (question_type == 'FRQ'):

				writer.writerow([
					'Last Name',
					'First Name',
					'Gender',
					'Race',
					'Age',
					'Answer',
				])

				responses = FreeResponseAnswer.objects.filter(question=question)

				for r in responses: 
					print(r.answer)
					writer.writerow([
						smart_str(r.observer_report.user_profile.last_name),
						smart_str(r.observer_report.user_profile.first_name),
						smart_str(r.observer_report.user_profile.gender),
						smart_str(r.observer_report.user_profile.get_race_display()),
						smart_str(r.observer_report.user_profile.age),
						smart_str(r.answer),
					])

			if (question_type == 'SAQ'):

				writer.writerow([
					'Last Name',
					'First Name',
					'Gender',
					'Race',
					'Age',
					'Answer',
				])

				responses = SingleAnswerResponse.objects.filter(question=question)

				for r in responses:
					writer.writerow([
						smart_str(r.observer_report.user_profile.last_name),
						smart_str(r.observer_report.user_profile.first_name),
						smart_str(r.observer_report.user_profile.gender),
						smart_str(r.observer_report.user_profile.get_race_display()),
						smart_str(r.observer_report.user_profile.age),
						smart_str(r.answer),
					])

			if (question_type == 'MCQ'):
				possible_answers = question.get_options()

				build_row = ['Last Name', 'First Name', 'Gender', 'Race', 'Age',]

				for option in possible_answers:
					build_row.append(option)

				writer.writerow(build_row)

				responses = MultipleChoiceResponse.objects.filter(question=question)

				
				for r in responses:
					build_row = [smart_str(r.observer_report.user_profile.last_name), smart_str(r.observer_report.user_profile.first_name),smart_str(r.observer_report.user_profile.gender), smart_str(r.observer_report.user_profile.get_race_display()),smart_str(r.observer_report.user_profile.age),]
					all_answers = r.answer.all()
					for option in possible_answers:
						if (option in all_answers):
							build_row.append(option)
						else:
							build_row.append('')

					writer.writerow(build_row)


			if (question_type == 'GQ'):
				#get the sub prompts
				prompts = question.get_prompts()
				for prompt in prompts:
					writer.writerow([
						prompt,
					])

					writer.writerow([
						'Last Name',
						'First Name',
						'Gender',
						'Race',
						'Age',
						'Answer',
					])

					responses = GridQuestionResponse.objects.filter(prompt=prompt)

					for r in responses:
						writer.writerow([
							smart_str(r.observer_report.user_profile.last_name),
							smart_str(r.observer_report.user_profile.first_name),
							smart_str(r.observer_report.user_profile.gender),
							smart_str(r.observer_report.user_profile.get_race_display()),
							smart_str(r.observer_report.user_profile.age),
							smart_str(r.answer),
						])
			

			writer.writerow([''])

	return response



def clone_observation(modeladmin,request,queryset):
	for ob in queryset:
		old_questions = ob.get_questions()
		ob.pk = None
		ob.is_active = True
		ob.title = ob.title + ' copy'
		ob.save()
		for question in old_questions:
			if (isinstance(question,FreeResponseQuestion)):
				question.pk = None
				question.id = None
				question.observation = ob
				question.save()
			elif (isinstance(question,SingleAnswerQuestion)):
				options = SingleAnswerOption.objects.filter(question=question)
				question.pk = None
				question.id = None
				question.observation = ob
				question.save()
				new_question = question
				for option in options:
					option.pk = None
					option.id = None
					option.question = new_question
					option.save()
			elif (isinstance(question,MultipleChoiceQuestion)):
				options = MultipleChoiceOption.objects.filter(question=question)
				question.pk = None
				question.id = None
				question.observation = ob
				question.save()
				new_question = question
				for option in options:
					option.pk = None
					option.id = None
					option.question = new_question
					option.save()
			elif (isinstance(question,GridQuestion)):
				prompt_set = GridQuestionPrompt.objects.filter(question=question)
				option_set = GridQuestionOption.objects.filter(question=question)
				question.pk = None
				question.id = None
				question.observation = ob
				question.save()
				new_question = question
				
				for option in option_set:
					option.pk = None
					option.id = None
					option.question = new_question
					option.save()

				for option in prompt_set:
					option.pk = None
					option.id = None
					option.question = new_question
					option.save()

def show_observer_reports(modeladmin, request, queryset):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="observer_reports.csv"'

	writer = csv.writer(response, csv.excel)

	for observer in queryset: #UserProfile
		
		writer.writerow([
			observer,
		])	

		# reports = ObserverReport.objects.all().order_by().values_list('committee_number', flat=True).distinct().order_by('committee_number')
		#reports = observer.observerreport_set.all().order_by().values_list('observation_start_date')
		reports = ObserverReport.objects.filter(user_profile=observer)
		for report in reports:
			
			writer.writerow([
					'Observer Report:', 
					report.observation,
					report.observation_start_date,
					report.observation_end_date,
				])

			tallys = Tally.objects.filter(tally_report=report).order_by('member__last_name', 'member__first_name')
			print(tallys)
			if tallys is not None:
				writer.writerow([
					'Committee Number', 
					'Member Last Name',
					'Member First Name',
					'Observation Date',
					'Tally',
				])
				for tally in tallys:
					writer.writerow([
						smart_str(tally.tally_report.committee_number),
						smart_str(tally.member.last_name),
						smart_str(tally.member.first_name),
						smart_str(tally.tally_report.observation_start_date),
						smart_str(tally.count),
	        		])

				writer.writerow([''])

	return response


class FreeResponseQuestionInline(SortableInlineAdminMixin,admin.StackedInline):
	model = FreeResponseQuestion
	fieldsets = [
		(None, {'fields':['prompt','sort_order']})
	]

class MultipleChoiceOptionInline(admin.StackedInline):
	model = MultipleChoiceOption

class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
	model = MultipleChoiceQuestion
	inlines = [
	  MultipleChoiceOptionInline,
	]

class MultipleChoiceQuestionInline(admin.StackedInline):
	model = MultipleChoiceQuestion
	fieldsets = [
		(None, {'fields':['prompt','sort_order']})
	]

class SingleAnswerOptionInline(admin.StackedInline):
	model = SingleAnswerOption

class SingleAnswerQuestionInline(admin.StackedInline):
	model = SingleAnswerQuestion

class SingleAnswerQuestionAdmin(admin.ModelAdmin):
	model = SingleAnswerQuestion
	inlines = [
	  SingleAnswerOptionInline,
	]

class GridQuestionOptionInline(admin.StackedInline):
	model = GridQuestionOption

class GridQuestionPromptInline(admin.StackedInline):
	model = GridQuestionPrompt

class GridQuestionInline(admin.StackedInline):
	model = GridQuestion


class GridQuestionAdmin(admin.ModelAdmin):
	model = GridQuestion
	inlines = [
		GridQuestionOptionInline, GridQuestionPromptInline
	]


class ObservationAdmin(admin.ModelAdmin):
	actions = [clone_observation, pull_all_responses, pull_all_tallys]


class QuestionAdmin(SortableAdminMixin,admin.ModelAdmin):
	list_filter = ('observation',)
	list_display = ('sort_order','prompt','change_link')

	def change_link(self, result):		
		pk = result.id
		question_type = result.question_type()		
		question_type_url = 'question'
		if question_type == 'FRQ':
			question_type_url = 'freeresponsequestion'
		elif question_type == 'SAQ':
			question_type_url = 'singleanswerquestion'
		elif question_type == 'MCQ':
			question_type_url = 'multiplechoicequestion'
		elif (question_type == 'GQ'):
			question_type_url = 'gridquestion'
		
		return '<a href="/siteadmin/base/%s/%d/">Edit Question</a>' % (question_type_url, quote(pk))

	change_link.allow_tags = True
	change_link.short_description = 'Edit Question'

	class Media:
	    js = ('base/question_tools.js',)

	

class TallyAdmin(admin.ModelAdmin):
	list_filter = ('tally_report',)

class ObserverReportInline(admin.TabularInline):
	model = ObserverReport	
	extra=0
	max_num=0
	fields=['observation_start_date', 'observation_end_date', 'committee_number']
	readonly_fields=['committee_number', 'observation_start_date', 'observation_end_date']
	show_change_link=True

class UserProfileAdmin(admin.ModelAdmin):
	# def queryset(self,request):
	# 	return super(UserProfileAdmin, self).queryset(request).filter(pk=1)#user__is_superuser=False

	actions = [show_observer_reports]	

	inlines = [
		ObserverReportInline
	]

	class Media:
	    js = ('base/observer_tools.js',)

class ObserverReportAdmin(admin.ModelAdmin):	
	
	class Media:
	    js = ('base/observer_report_tools.js',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Observation, ObservationAdmin)
admin.site.register(ObserverReport, ObserverReportAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(FreeResponseQuestion)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceQuestionAdmin)
admin.site.register(SingleAnswerQuestion, SingleAnswerQuestionAdmin)
admin.site.register(GridQuestion, GridQuestionAdmin)
admin.site.register(CommitteeMember)
admin.site.register(Tally, TallyAdmin)