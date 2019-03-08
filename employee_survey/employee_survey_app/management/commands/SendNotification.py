from django.core.management.base import BaseCommand, CommandError
from employee_survey.employee_survey_app import EmailModel
from employee_survey.employee_survey_app.models import SurveyUser, User
import datetime


class Command(BaseCommand):
    help = 'Type the help text here'

    def handle(self, *args, **options):
        self.send_notification_one_day_prior()
        self.send_notification_on_start_date()
        self.send_notification_one_day_before_end_date()
        self.send_notification_after_end_date()

    @staticmethod
    def send_notification_one_day_prior():
        upcoming = SurveyUser.objects.filter(start_date=datetime.date.today() + datetime.timedelta(days=1))
        for employee in upcoming:
            try:
                emp = User.objects.get(pk=employee.user_id)
                print(" i m i upcoming name ", emp.first_name, "Email", emp.email)
                subject = 'You have a new survey coming tomorrow.'
                body = "Hello {}<br><br> ".format(emp.first_name)
                body += "You have a new survey coming tomorrow.<br>"
                body += "Please login to survey management and complete your survey.<br><br>"
                body += "Thanks,<br>{}".format("Survey Management Team")
                EmailModel.send_mail_fun(subject, body, [emp.email])
            except Exception as e:
                print(" Exception in Upcoming Survey ", e)

    @staticmethod
    def send_notification_on_start_date():
        started = SurveyUser.objects.filter(start_date=datetime.date.today())
        for employee in started:
            try:
                emp = User.objects.get(pk=employee.user_id)
                print(" i m i start_date name ", emp.first_name, "Email", emp.email)
                subject = 'You have a new survey in your dashboard.'
                body = "Hello {}<br><br> ".format(emp.first_name)
                body += "You have a new survey in your dashboard.<br>"
                body += "Please login to survey management and complete your survey.<br><br>"
                body += "Thanks,<br>{}".format("Survey Management Team")
                EmailModel.send_mail_fun(subject, body, [emp.email])
            except Exception as e:
                print(" Exception in start_date Notification ", e)

    @staticmethod
    def send_notification_one_day_before_end_date():
        started = SurveyUser.objects.filter(end_date=datetime.date.today() + datetime.timedelta(days=1))
        for employee in started:
            try:
                emp = User.objects.get(pk=employee.user_id)
                print(" i m i one_day_before_end_date name ", emp.first_name, "Email", emp.email)
                subject = 'Survey assigned to you ending tomorrow.'
                body = "Hello {}<br><br> ".format(emp.first_name)
                body += "Survey in your dashboard ending tomorrow.<br>"
                body += "Please login to survey management and complete your survey.<br><br>"
                body += "Thanks,<br>{}".format("Survey Management Team")
                EmailModel.send_mail_fun(subject, body, [emp.email])
            except Exception as e:
                print(" Exception in before_end_date Notification ", e)

    @staticmethod
    def send_notification_after_end_date():
        started = SurveyUser.objects.filter(end_date__lt=datetime.date.today())
        for employee in started:
            try:
                emp = User.objects.get(pk=employee.user_id)
                print(" i m i after_end_date name ", emp.first_name, "Email", emp.email)
                subject = 'Survey assigned to you was ended.'
                body = "Hello {}<br><br> ".format(emp.first_name)
                body += "Survey in your dashboard ended.<br>"
                body += "Please login to survey management and complete your survey.<br><br>"
                body += "Thanks,<br>{}".format("Survey Management Team")
                EmailModel.send_mail_fun(subject, body, [emp.email])
            except Exception as e:
                print(" Exception in after_end_date Notification ", e)


