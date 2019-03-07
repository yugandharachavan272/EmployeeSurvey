from django.shortcuts import render
from .forms import UserForm, UserSurveyAssignmentForm
# from .models import UserProfileInfo
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import View, TemplateView, ListView, DetailView
from employee_survey_app import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail, EmailMessage
from employee_survey_app import EmailModel
from .errors import *
# import settings

from .models import Question, Survey, Category, Response, AnswerBase
from django.contrib.auth.models import User
from .forms import ResponseForm
from django.contrib.auth import get_user_model
User = get_user_model()


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
            response = Response.objects.all()
        elif request.user.groups.filter(name='SuperAdmin').exists():
            response = Response.objects.all()
        elif request.user.groups.filter(name='OrganisationAdmin').exists():
            print(" i  m in org admin")
            response = Response.objects.filter(user__organisation_id=request.user.organisation_id)
        else:
            response = Response.objects.filter(user_id=request.user.id)
    else:
        response = Response.objects.filter(user_id=request.user.id)
    return render(request, 'employee_survey_app/survey_report.html', {'response': response})


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        # profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid():
            # and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            # profile = profile_form.save(commit=False)
            # profile.user = user
            # if 'profile_pic' in request.FILES:
            #     print('found it')
            #     profile.profile_pic = request.FILES['profile_pic']
            # profile.save()
            registered = True
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()
        # profile_form = UserProfileInfoForm()
    return render(request, 'employee_survey_app/registration.html',
                  {'user_form': user_form,
                           # 'profile_form': profile_form,
                           'registered': registered})


def user_survey_assignment(request):
    if request.method == 'POST':
        user_survey_form = UserSurveyAssignmentForm(data=request.POST)
        if user_survey_form.is_valid():
            userssurvey = user_survey_form.save()
            userssurvey.save()
            data = request.POST.copy()
            try:
                user_id = data.get('user')
                survey_id = data.get('survey')
                user = User.objects.get(id=user_id)
                survey = Survey.objects.get(id=survey_id)
                print("user ", user.username, "survey ", survey.name, "Email", user.email)
                # send_mail('subject', 'Employee Survey', 'sender@example.com',
                #          ['receiver1@example.com', 'receiver2@example.com'])
                # email = EmailMessage('Employee Survey', "You have assigned new survey", survey.name, to=[user.email])
                # email.send()
                subject = "Assignment of Survey"
                sms_text = "You have assigned new survey", survey.name
                email_to = [user.email]
                EmailModel.send_mail_fun(subject, sms_text, email_to)
            except Exception as e:
                print("Exception in email", e)

            return HttpResponse("Assignment Done Successfully")
    else:
        user_survey_form = UserSurveyAssignmentForm()
    return render(request, 'employee_survey_app/UsersSurveyAssignment.html', {'user_survey_form': user_survey_form})


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
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'employee_survey_app/login.html', {})


def survey_detail(request, id ):
    survey = Survey.objects.get(id=id)
    category_items = Category.objects.filter(survey=survey)
    categories = [c.name for c in category_items]
    # print("categories for this survey:")
    user = request.user
    is_finished = False
    response_id = 0
    comments = ""
    if request.method == 'POST':
        if 'save_btn' in request.POST:
            # do subscribe
            is_finished = False
        elif 'finish_btn' in request.POST:
            is_finished = True

        try:
            user_response = Response.objects.get(survey=survey, user=user)
            response_id = user_response.id
        except Exception as e:
            response_id = 0
            print(" i m in exception ", e)

        if response_id:
            f = Response.objects.get(pk=response_id)
            form = ResponseForm(request.POST, request.FILES, instance=f, survey=survey, user=user,
                                is_finished=is_finished,
                                user_Response_id=response_id)
        else:
            form = ResponseForm(request.POST, survey=survey, user=user,
                                is_finished=is_finished,
                                user_Response_id=response_id)

        # print("i m in form submit")
        if form.is_valid():
            response = form.save()
            if is_finished:
                # print("user ", user.username, "survey ", survey.name, "Email", user.email)
                subject = "Complete Survey : ", survey.name
                sms_text = "Hello ", user.username, ", \n Thank you for completing survey ", survey.name, "."
                email_to = [user.email]
                EmailModel.send_mail_fun(subject, sms_text, email_to)

            return HttpResponseRedirect("/employee_survey_app/confirm/%s" % response.interview_uuid)
    else:
        # print("i m in else")
        data = dict()
        try:
            user_response = Response.objects.get(survey=survey, user=user)
            response_id = user_response.id
            comments = user_response.comments
        except Exception as e:
            response_id = 0
            print(" i m in exception ", e)

        form = ResponseForm(survey=survey, user=user, is_finished=False, user_Response_id=response_id,
                            initial={'user': user, 'comments': comments})
        # print(form)
        # TODO sort by category
    return render(request, 'employee_survey_app/survey.html', {'response_form': form, 'survey': survey,
                                                               'categories': categories, 'user': user,
                                                               'is_finished': False, 'user_Response_id': response_id})


def confirm(request, uuid):
    # email = settings.support_email
    # return render(request, 'confirm.html', {'uuid': uuid, "email":email })
    return render(request, 'employee_survey_app/confirm.html', {'uuid': uuid})


class EmployeeSurveys(LoginRequiredMixin, ListView):
    context_object_name = 'UsersSurveys'
    model = models.SurveyUser
    template_name = 'employee_survey_app/employee_surveys.html'
    # paginate_by = 5

    def get_queryset(self):
        return models.Survey.objects.filter(user=self.request.user)
