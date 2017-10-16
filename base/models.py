from __future__ import unicode_literals

import datetime

from django.db import models
from django.conf import settings
from django.db.models import signals
from django.dispatch import dispatcher

from django.db.models.signals import post_save


from polymorphic.models import PolymorphicModel


#defining the choices for the gender
GENDER_CHOICES = (
    ('F','Female'),
    ('M', 'Male'),
    ('O', 'Other'),
)

#defining the choices for the race field
RACE_CHOICE_WHITE = 'W'
RACE_CHOICE_BLACK = 'B'
RACE_CHOICE_HISPANIC = 'H'
RACE_CHOICE_ASIAN = 'A'
RACE_CHOICE_NATIVE_AMERICAN = 'N'
RACE_CHOICE_MIDDLE_EASTERN = 'M'
RACE_CHOICE_MULTI = 'R'

RACE_CHOICES = (
    (RACE_CHOICE_WHITE,'White, Euro-American'),
    (RACE_CHOICE_BLACK, 'Black, African American'),
    (RACE_CHOICE_HISPANIC, 'Hispanic, Latin'),
    (RACE_CHOICE_ASIAN, 'Asian, Pacific Islander'),
    (RACE_CHOICE_NATIVE_AMERICAN, 'Native American, American Indian'),
    (RACE_CHOICE_MIDDLE_EASTERN, 'Middle Eastern'),
    (RACE_CHOICE_MULTI, 'Multiracial (more than 1 previous category)'),
)


# This model is for Observers, not committee members
# Not sure yet if we are importing the committee members, or pulling
#  them live from an API
class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, to_field='id', null=True, related_name='userprofile')
    # birth_date = models.DateField(blank=True,null=True)
    age = models.PositiveSmallIntegerField(blank=False, null=True, help_text='Enter your age as of June 18,2016')
    gender = models.CharField(max_length=50,choices=GENDER_CHOICES,default='F')
    race = models.CharField(max_length=50,choices=RACE_CHOICES,default='W')
    email = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50, blank=False, null=True)
    last_name = models.CharField(max_length=50, blank=False, null=True)
    
    def __str__(self):
        fname = '(empty)'
        lname = '(empty)'
        if self.first_name is not None:
            fname = self.first_name
        if self.last_name is not None:
            lname = self.last_name
        return fname + ' ' + lname #+ '(' + self.id + ')'

    class Meta:
        verbose_name = "Observer"
        verbose_name_plural = "Observers"

#This is the model for the set of questions for the current form
class Observation(models.Model):
    id = models.AutoField(primary_key=True)
    is_active = models.BooleanField(default=True)
    title = models.CharField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            try:
                temp = Observation.objects.get(is_active=True)
                if self != temp:
                    temp.is_active = False
                    temp.save()
            except Observation.DoesNotExist:
                pass
        super(Observation,self).save(*args,**kwargs)


    def get_questions(self):
        question_set = Question.objects.filter(observation=self.id).order_by('sort_order')
        return question_set

    def __str__(self):
        is_active_str = ''
        if self.is_active:
            is_active_str = ' (active)'
            
        if self.title:
            return self.title + is_active_str
        else:
            return 'Please add title' + is_active_str

    class Meta:
        verbose_name = "Observation"
        verbose_name_plural = "  Observations"


class ObserverReport(models.Model):
    user_profile = models.ForeignKey(UserProfile)
    observation = models.ForeignKey(Observation)
    created_date = models.DateTimeField(auto_now=True)
    observation_start_date = models.DateTimeField(blank=True, null=True)
    observation_end_date = models.DateTimeField(blank=True, null=True)
    committee_number = models.IntegerField(blank=False,null=True)
    recorded_tally_start_date = models.DateTimeField(blank=True, null=True)
    recorded_tally_observation_end_date = models.DateTimeField(blank=True, null=True)

    def get_responses(self):
        response_set = Response.objects.filter(observer_report=self.id)
        return response_set

    def __str__(self):        
        return str(self.observation)



#define choices for identities and age
COMMITTEE_MEMBER_RACE_CHOICES = [
    ['W', ['white']],
    ['A', ['asian','american','pacific','islander']],
    ['B', ['african', 'american']],
    ['H', ['hispanic', 'latino']],
    ['N', ['native', 'american']],
    ['M', ['middle', 'eastern']],
    ['O', ['other']],
]

COMMITTEE_MEMBER_GENDER_CHOICES = [
    ['F', ['female']],
    ['M', ['male']],
]

COMMITTEE_MEMBER_ROLE_CHOICES = [
    ['R', ['ruling','elder','commissioner']],
    ['T', ['teaching','elder','commissioner']],
    ['Y', ['young', 'adult','advisory','delegate']],
    ['S', ['theological', 'student','advisory','delegate']],
    ['M', ['mission', 'advisory','delegate']],
    ['E', ['ecumenical', 'advisory','delegate']],
]

def value_for_choices(string, choices):
    if not string: #if string is not a value, return '_'
        return '_'
    for value, keywords in choices:
        isMatch = True
        for keyword in keywords:
            if keyword.lower() not in string.lower():
                isMatch = False
        if isMatch:
            return value

    #no matches, return '_'
    return '_'

#This model represents the commissioners we are pulling from the API
class CommitteeMember(models.Model):
    id = models.AutoField(primary_key=True)
    commissioner_id = models.IntegerField(unique=True,null=True)
    first_name = models.CharField(max_length=51, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    badge_name = models.CharField(max_length=50, blank=True, null=True)
    display_name = models.CharField(max_length=50, blank=True, null=True)
    presbytery = models.CharField(max_length=200,blank=True,null=True)
    gender = models.CharField(max_length=50,blank=True,null=True)
    race = models.CharField(max_length=200,blank=True,null=True)
    age = models.IntegerField(blank=True,null=True)
    role = models.CharField(max_length=200,blank=True,null=True)
    secondary_role = models.CharField(max_length=200,blank=True,null=True)
    has_special_needs = models.BooleanField(default=False)
    needs_translation = models.BooleanField(default=False)

    def identities_indicator(self):
        identitiesString = ''

        race = value_for_choices(self.race, COMMITTEE_MEMBER_RACE_CHOICES)
        identitiesString += race
        gender = value_for_choices(self.gender, COMMITTEE_MEMBER_GENDER_CHOICES)
        identitiesString += gender
        role = value_for_choices(self.role, COMMITTEE_MEMBER_ROLE_CHOICES)
        identitiesString += role

        identitiesString += ' '

        if(self.has_special_needs):
            identitiesString += 'Y'
        else:
            identitiesString += '_'

        if(self.needs_translation):
            identitiesString += 'Y'
        else:
            identitiesString += '_'

        identitiesString += ' '

        identitiesString += str(self.age_indicator())

        return identitiesString

    def get_role_abbreviation(self):
        abbreviation = ''
        role = value_for_choices(self.role, COMMITTEE_MEMBER_ROLE_CHOICES)
        if(role):
            if (role == 'R'):
                abbreviation = 'REC'
            elif (role == 'T'):
                abbreviation = 'TEC'
            elif (role == 'Y'):
                abbreviation = 'YAAD'
            elif (role == 'S'):
                abbreviation = 'TSAD'
            elif (role == 'M'):
                abbreviation = 'MAD'
            elif (role == 'E'):
                abbreviation = 'EAD'

        return abbreviation

    def age_indicator(self):
        ageNumber = 9;

        if self.age:
            if self.age < 25:
                ageNumber = 1
            elif self.age < 35:
                ageNumber = 2
            elif self.age < 45:
                ageNumber = 3
            elif self.age < 55:
                ageNumber = 4
            elif self.age < 65:
                ageNumber = 5
            elif self.age < 75:
                ageNumber = 6
            elif self.age < 85:
                ageNumber = 7
            elif self.age >= 85:
                ageNumber = 8
            
        return ageNumber

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' ' + '(' + self.identities_indicator() + ')' + ' Age Level: ' + str(self.age_indicator())

#This model tracks the count of how many times a commissioner spoke during an observation (an ObservationReport)
class Tally(models.Model):
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(CommitteeMember)
    tally_report = models.ForeignKey(ObserverReport)
    count = models.PositiveSmallIntegerField(blank=False,null=True,default=0) 

    def __str__(self):
        return self.member.first_name + ' ' + self.member.last_name + ' ' + str(self.tally_report)



#This is the model for the form
class Question(PolymorphicModel):
    id = models.AutoField(primary_key=True)
    observation = models.ForeignKey(Observation)
    prompt = models.CharField(max_length=2000, blank=False, null=True)
    sort_order = models.IntegerField(default=0)

    def question_type(self):
        question_type = 'FRQ'
        if (isinstance(self,FreeResponseQuestion)):
            pass
        elif (isinstance(self,SingleAnswerQuestion)):
            question_type = 'SAQ'
        elif (isinstance(self,MultipleChoiceQuestion)):
            question_type = 'MCQ'
        elif (isinstance(self,GridQuestion)):
            question_type = 'GQ'

        return question_type

    def __str__(self):
        return self.prompt

    class Meta():
        ordering=('sort_order',)

        verbose_name = "Question"
        verbose_name_plural = " Questions"

class FreeResponseQuestion(Question):
    pass



class MultipleChoiceQuestion(Question):
    pass

    def get_options(self):
        options_set = MultipleChoiceOption.objects.filter(question=self.id)
        return options_set

class MultipleChoiceOption(models.Model):
    question = models.ForeignKey(MultipleChoiceQuestion)
    option = models.CharField(max_length=200,blank=False)

    def __str__(self):
        return self.option


class SingleAnswerQuestion(Question):
    pass

    def get_options(self):
        options_set = SingleAnswerOption.objects.filter(question=self.id).order_by('pk')
        return options_set

class SingleAnswerOption(models.Model):
    question = models.ForeignKey(SingleAnswerQuestion)
    option = models.CharField(max_length=200,blank=False)

    def __str__(self):
        return self.option

class GridQuestion(Question):
    pass

    def get_prompts(self):
        prompt_set = GridQuestionPrompt.objects.filter(question=self.id).order_by('prompt_sort_order')
        return prompt_set

    def get_options(self):
        option_set = GridQuestionOption.objects.filter(question=self.id).order_by('option_sort_order')
        return option_set

class GridQuestionPrompt(models.Model):
    question = models.ForeignKey(GridQuestion, related_name='header', help_text='These will be the possible answers for the sub-prompts')
    sub_prompt = models.CharField(max_length=2000, blank=False, null=True)
    prompt_sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.sub_prompt

class GridQuestionOption(models.Model):
    question = models.ForeignKey(GridQuestion)
    option = models.CharField(max_length=200,blank=False)
    option_sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.option

class Response(PolymorphicModel):
    question = models.ForeignKey(Question)
    observer_report = models.ForeignKey(ObserverReport)
    on_form = models.BooleanField(default=True)

    def __str__(self):
        return self.question.prompt + '%s' % self.id

class FreeResponseAnswer(Response):
    answer = models.TextField(blank=False,default='N/A')

class SingleAnswerResponse(Response):
    answer = models.ForeignKey(SingleAnswerOption, null=True,blank=False)


class MultipleChoiceResponse(Response):
    answer = models.ManyToManyField(MultipleChoiceOption)

class GridQuestionResponse(Response):
    prompt = models.ForeignKey(GridQuestionPrompt, null=True, blank=True)
    answer = models.ForeignKey(GridQuestionOption, null=True, blank=True)


#After we create the ObserverReport automatically create all the responses
# we need to fill in the form
#
#If the Observation is changed after the creation of the Report - the ObserverReport will not reflect those changes 
def create_responses(sender, **kwargs):
    if kwargs['created'] == True: #JR - added this to prevent this method from being run every time the observer_report is modified and then saved
        report = kwargs['instance']
        question_set = report.observation.get_questions()
        for question in question_set:
            if (isinstance(question,FreeResponseQuestion)):
                response = FreeResponseAnswer.objects.create(question=question, observer_report=report)
            elif (isinstance(question,SingleAnswerQuestion)):
                response = SingleAnswerResponse.objects.create(question=question, observer_report=report)
            elif (isinstance(question,MultipleChoiceQuestion)):
                response= MultipleChoiceResponse.objects.create(question=question, observer_report=report)
            elif (isinstance(question,GridQuestion)):
                response = GridQuestionResponse.objects.create(question=question, observer_report=report)

        responses = report.get_responses()
        print (responses)

post_save.connect(create_responses,ObserverReport)










