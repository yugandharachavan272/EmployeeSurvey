# pylint: disable=invalid-name
# pylint: disable=missing-docstring
from django.conf.urls import url
from . import views

# SET THE NAMESPACE!
app_name = 'employee_survey_app'
# Be careful setting the name to just /login use userlogin instead!
urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'user_survey_assignment/$', views.user_survey_assignment, name='user_survey_assignment'),
    url(r'survey_report/$', views.survey_report, name='survey_report'),
    url(r'^user_login/$', views.user_login, name='user_login'),
    url(r'^my_surveys/$', views.EmployeeSurveys.as_view(), name='my_surveys'),
    # url(r'^my_surveys/(?P<id>[-\w]+)/$', views.survey_detail, name='detail'),
    url(r'^my_surveys/(?P<id>[-\w]+)/$', views.survey_detail, name='my_surveys_detail'),
    url(r'^confirm/(?P<uuid>\w+)/$', views.confirm, name='confirmation')
]
