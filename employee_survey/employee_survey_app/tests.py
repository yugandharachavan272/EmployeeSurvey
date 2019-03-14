from django.test import TestCase
from .forms import UserForm, ResponseForm
from .models import User, Organisation


# Create your tests here.
class SetupClass(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@mp.com", password="user", first_name="user", username="test user")


class UserFormTest(TestCase):

    # Valid Form Data
    def test_UserForm_valid(self):
        form = UserForm(data={'username': "user", 'password': "user", 'email': "user@mp.com"})
        self.assertTrue(form.is_valid())

    # Invalid Form Data
    def test_UserForm_invalid(self):
        form = UserForm(data={'username': "", 'password': "mp", 'email': ""})
        self.assertFalse(form.is_valid())


class OrganizationTest(TestCase):
    @staticmethod
    def create_organization(name="company for test"):
        return Organisation.objects.create(name=name)

    def test_org_creation(self):
        w = self.create_organization()
        self.assertTrue(isinstance(w, Organisation))
        self.assertEqual(w.__str__(), w.name)
