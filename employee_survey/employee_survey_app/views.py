# pylint: disable=invalid-name
# pylint: disable=broad-except
# pylint: disable=missing-docstring
# pylint: disable=no-member
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
import logging
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from datetime import date
from django.contrib.auth import get_user_model
from employee_survey_app import models
from employee_survey_app import EmailModel
from .forms import UserForm, UserSurveyAssignmentForm, ResponseForm
from .models import Survey, Category, Response, SurveyUser, Organisation

User = get_user_model()
# Get an instance of a logger
logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'employee_survey_app/index.html')


@login_required
def special(request):
    return HttpResponse("You are logged in !")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def survey_report(request):
    if request.user.is_staff:
        if request.user.is_superuser:
            result = SurveyUser.objects.all()
            response = list()
            for i in result:
                obj = dict()
                obj['id'] = i.id
                obj['survey'] = i.survey
                obj['user'] = i.user
                obj['start_date'] = i.start_date
                obj['end_date'] = i.end_date
                obj['is_past_end_date'] = date.today() > i.end_date
                is_response = Response.objects.filter(survey_user_id=i.id)
                if is_response:
                    obj['response'] = is_response[0]
                    response.append(obj)
                else:
                    response.append(obj)
        elif request.user.groups.filter(name='SuperAdmin').exists():
            # response = Response.objects.all()
            result = SurveyUser.objects.all()
            response = list()
            for i in result:
                obj = dict()
                obj['id'] = i.id
                obj['survey'] = i.survey
                obj['user'] = i.user
                obj['start_date'] = i.start_date
                obj['end_date'] = i.end_date
                obj['is_past_end_date'] = date.today() > i.end_date
                is_response = Response.objects.filter(survey_user_id=i.id)
                if is_response:
                    obj['response'] = is_response[0]
                    response.append(obj)
                else:
                    response.append(obj)
        elif request.user.groups.filter(name='OrganisationAdmin').exists():
            # response = Response.objects.filter(user__organisation_id=request.user.organisation_id)
            result = SurveyUser.objects.filter(user__organisation_id=request.user.organisation_id)
            response = list()
            for i in result:
                obj = dict()
                obj['id'] = i.id
                obj['survey'] = i.survey
                obj['user'] = i.user
                obj['start_date'] = i.start_date
                obj['end_date'] = i.end_date
                obj['is_past_end_date'] = date.today() > i.end_date
                is_response = Response.objects.filter(survey_user_id=i.id)
                if is_response:
                    obj['response'] = is_response[0]
                    response.append(obj)
                else:
                    response.append(obj)
        else:
            # response = Response.objects.filter(user_id=request.user.id)
            result = SurveyUser.objects.filter(user_id=request.user.id)
            response = list()
            for i in result:
                obj = dict()
                obj['id'] = i.id
                obj['survey'] = i.survey
                obj['user'] = i.user
                obj['start_date'] = i.start_date
                obj['end_date'] = i.end_date
                obj['is_past_end_date'] = date.today() > i.end_date
                is_response = Response.objects.filter(survey_user_id=i.id)
                if is_response:
                    obj['response'] = is_response[0]
                    response.append(obj)
                else:
                    response.append(obj)
    else:
        # response = Response.objects.filter(user_id=request.user.id)
        result = SurveyUser.objects.filter(user_id=request.user.id)
        response = list()
        for i in result:
            obj = dict()
            obj['id'] = i.id
            obj['survey'] = i.survey
            obj['user'] = i.user
            obj['start_date'] = i.start_date
            obj['end_date'] = i.end_date
            obj['is_past_end_date'] = date.today() > i.end_date
            is_response = Response.objects.filter(survey_user_id=i.id)
            if is_response:
                obj['response'] = is_response[0]
                response.append(obj)
            else:
                response.append(obj)
    return render(request, 'employee_survey_app/survey_report.html', {'response': response})


def register(request):
    registered = False
    user = request.user
    if request.method == 'POST':
        user_form = UserForm(logged_in_user=user, data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
        else:
            logger.exception("Exception in user_form", user_form.errors)
    else:
        user_form = UserForm(logged_in_user=user)
        if request.user.is_staff and not request.user.is_superuser:
            if request.user.groups.filter(name='OrganisationAdmin').exists():
                user_form = UserForm(logged_in_user=user, initial={'organisation': request.user.organisation_id})

    return render(request, 'employee_survey_app/registration.html',
                  {'user_form': user_form, 'logged_in_user': user, 'registered': registered})


def user_survey_assignment(request):
    if request.method == 'POST':
        user_survey_form = UserSurveyAssignmentForm(data=request.POST)
        if user_survey_form.is_valid():
            users_survey = user_survey_form.save()
            users_survey.save()
            data = request.POST.copy()
            try:
                user_id = data.get('user')
                survey_id = data.get('survey')
                user = User.objects.get(id=user_id)
                survey = Survey.objects.get(id=survey_id)
                subject = "Assignment of Survey"
                sms_text = "You have assigned new survey", survey.name
                email_to = [user.email]
                EmailModel.send_mail_fun(subject, sms_text, email_to)
            except Exception as e:
                logger.exception("Exception in Assign users to survey", e)

            return HttpResponse("Assignment Done Successfully")
    else:
        user_survey_form = UserSurveyAssignmentForm()
    return render(request, 'employee_survey_app/UsersSurveyAssignment.html',
                  {'user_survey_form': user_survey_form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'employee_survey_app/login.html', {})


def survey_detail(request, id):
    survey_user_id = id
    survey_user = SurveyUser.objects.get(id=survey_user_id)
    is_past_end_date = date.today() >= survey_user.end_date
    survey = Survey.objects.get(id=survey_user.survey_id)
    # category_items = Category.objects.filter(survey=survey)
    # categories = [c.name for c in category_items]
    user = request.user
    is_finished = False
    comments = ""
    if request.method == 'POST':
        if 'save_btn' in request.POST:
            is_finished = False
        elif 'finish_btn' in request.POST:
            is_finished = True

        try:
            user_response = Response.objects.get(survey=survey, user=user, survey_user_id=survey_user_id)
            response_id = user_response.id
        except Exception as e:
            response_id = 0
            logger.exception("Exception in survey_detail - response_id", e)

        if response_id:
            f = Response.objects.get(pk=response_id)
            form = ResponseForm(request.POST, request.FILES, instance=f, survey=survey,
                                user=user, is_finished=is_finished, user_response_id=response_id,
                                is_past_end_date=is_past_end_date, survey_user_id=survey_user_id)
        else:
            form = ResponseForm(request.POST, survey=survey, user=user,
                                is_finished=is_finished, is_past_end_date=is_past_end_date,
                                user_response_id=response_id, survey_user_id=survey_user_id)

        if form.is_valid():
            response = form.save()
            if is_finished:
                subject = "Complete Survey : ", survey.name
                sms_text = "Hello ", user.username, ", \n Thank you for completing survey ",\
                           survey.name, "."
                email_to = [user.email]
                EmailModel.send_mail_fun(subject, sms_text, email_to)

            return HttpResponseRedirect("/employee_survey_app/confirm/%s"
                                        % response.interview_uuid)
    else:
        try:
            user_response = Response.objects.get(survey=survey, user=user, survey_user_id=survey_user_id)
            response_id = user_response.id
            comments = user_response.comments
        except Exception as e:
            response_id = 0
            logger.exception("Exception in survey_detail - GET ", e)

        form = ResponseForm(survey=survey, user=user, is_finished=False,
                            user_response_id=response_id, survey_user_id=survey_user_id,
                            is_past_end_date=is_past_end_date,
                            initial={'user': user, 'comments': comments})

        # TODO sort by category
    return render(request, 'employee_survey_app/survey.html',
                  {'response_form': form, 'survey': survey,
                   'user': user, 'is_finished': False,
                   'user_response_id': response_id, 'survey_user_id': survey_user_id,
                   'is_past_end_date': is_past_end_date})


def confirm(request, uuid):
    return render(request, 'employee_survey_app/confirm.html', {'uuid': uuid})


class EmployeeSurveys(LoginRequiredMixin, ListView):
    context_object_name = 'UsersSurveys'
    model = models.SurveyUser
    template_name = 'employee_survey_app/employee_surveys.html'
    # paginate_by = 5

    def get_queryset(self):

        result = SurveyUser.objects.filter(user_id=self.request.user.id)
        response = list()
        for i in result:
            obj = dict()
            obj['id'] = i.id
            obj['survey'] = i.survey
            obj['user'] = i.user
            obj['start_date'] = i.start_date
            obj['end_date'] = i.end_date
            obj['is_past_end_date'] = date.today() > i.end_date
            obj['is_past_start_date'] = date.today() >= i.start_date
            is_response = Response.objects.filter(survey_user_id=i.id)
            if is_response:
                obj['response'] = is_response[0]
                response.append(obj)
            else:
                response.append(obj)

        return response  # models.SurveyUser.objects.filter(user=self.request.user)
