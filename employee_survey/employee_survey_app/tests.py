from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission, Group
from .forms import UserForm, ResponseForm
from .models import User, Organisation, Category, Survey


# Create your tests here.
class SetupClass(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@mp.com", password="user", first_name="user", username="test user")


# Test Cases for form
class UserFormTest(TestCase):

    # Valid Form Data
    def test_UserForm_valid(self):
        form = UserForm(data={'username': "user", 'password': "user", 'email': "user@mp.com"})
        self.assertTrue(form.is_valid())

    # Invalid Form Data
    def test_UserForm_invalid(self):
        form = UserForm(data={'username': "", 'password': "mp", 'email': ""})
        self.assertFalse(form.is_valid())


# Model Test Cases
class OrganizationTest(TestCase):
    @staticmethod
    def create_organization(name="company for test"):
        return Organisation.objects.create(name=name)

    def test_org_creation(self):
        w = self.create_organization()
        self.assertTrue(isinstance(w, Organisation))
        self.assertEqual(w.__str__(), w.name)


class CategoryTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(name='test survey')

    @staticmethod
    def create_Category(name="company for test"):
        return Category.objects.create(name=name, survey_id=1)

    def test_org_creation(self):
        w = self.create_Category()
        self.assertTrue(isinstance(w, Category))
        self.assertEqual(w.__str__(), w.name)


#  View Test Cases
class SurveyReportTest(TestCase):
    def setUp(self):
        # Create two users
        test_organisation = Organisation.objects.create(name='test')
        test_user1 = User.objects.create_user(username='test_user', password='1X<ISRUkw+tuK', is_superuser=False,
                                              is_staff=True, organisation_id=test_organisation.id)
        test_user1.group = Group(name='OrganisationAdmin')
        test_user1.group.save()
        test_user1.save()

    def survey_report_test(self):
        # Check User is logged in and redirect
        response = self.client.get(reverse('employee_survey_app:survey_report'))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

        login = self.client.login(username='test_user', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('employee_survey_app:survey_report'))
        # self.assertRedirects(response, '/employee_survey_app/user_login/?next=/employee_survey_app/survey_report/')

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'test_user')

        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('response' in response.context)

        # Confirm all survey belong to test_user
        for survey_item in response.context['response']:
            self.logged_in_user = response.context['user']
            if self.logged_in_user.is_staff:
                if self.logged_in_user.is_superuser:
                    pass
                elif self.logged_in_user.group.contains('SuperAdmin'):
                    pass
                elif self.logged_in_user.group.contains('OrganisationAdmin'):
                    self.assertEqual(response.context['user'].organisation_id, survey_item.organisation_id)
            else:
                self.assertEqual(response.context['user'], survey_item.user.id)

