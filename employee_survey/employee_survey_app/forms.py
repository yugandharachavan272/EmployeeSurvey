# pylint: disable=invalid-name
# pylint: disable=broad-except
# pylint: disable=missing-docstring
# pylint: disable=no-member
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
import uuid
import logging
from django import forms
from django.forms import models
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from .models import Question, Response, AnswerText, AnswerRadio,\
    AnswerSelect, AnswerInteger, AnswerSelectMultiple, \
    SurveyUser, AnswerBase


User = get_user_model()


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'organisation')


class UserSurveyAssignmentForm(forms.ModelForm):
    class Meta:
        model = SurveyUser
        fields = ('survey', 'user')


class HorizontalRadioRenderer(forms.RadioSelect):
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class ResponseForm(models.ModelForm):
    class Meta:
        model = Response
        fields = ('user', 'comments')

    def __init__(self, *args, **kwargs):
        # expects a survey object to be passed in initially
        survey = kwargs.pop('survey')
        user = kwargs.pop('user')
        is_finished = kwargs.pop('is_finished')
        user_response_id = kwargs.pop('user_response_id')
        self.user_response_id = user_response_id
        self.is_finished = is_finished
        self.user = user
        self.survey = survey
        super(ResponseForm, self).__init__(*args, **kwargs)
        self.uuid = uuid.uuid4().hex

        if user_response_id:
            survey_response = Response.objects.get(id=user_response_id)
            self.uuid = survey_response.interview_uuid
            self.created = survey_response.created
            self.updated = survey_response.updated

        # add a field for each survey question, corresponding to the question
        # type as appropriate.

        for q in survey.questions():
            if user_response_id:
                try:
                    response = AnswerBase.objects.get(response=user_response_id, question=q.pk)
                except Exception as e:
                    logging.exception("Exception in response form - AnswerBase: %s", e)
            if q.question_type == Question.TEXT:
                self.fields["question_%d" % q.pk] = \
                    forms.CharField(label=q.text, widget=forms.Textarea)
                try:
                    response = AnswerBase.objects.get(response=user_response_id, question=q.pk)
                    if response:
                        initial = AnswerText.objects.get(id=response.id)
                        self.fields["question_%d" % q.pk].initial = initial.body
                except Exception as e:
                    logging.exception("Exception in response form - AnswerText: %s", e)

            elif q.question_type == Question.RADIO:
                question_choices = q.get_choices()
                self.fields["question_%d" % q.pk] = forms.ChoiceField(label=q.text,
                                                                      widget=forms.RadioSelect(),
                                                                      choices=question_choices)
                try:
                    if response:
                        initial = AnswerRadio.objects.get(id=response.id)
                        self.fields["question_%d" % q.pk].initial = initial.body
                except Exception as e:
                    logging.exception("Exception in response form - AnswerRadio: %s", e)

            elif q.question_type == Question.SELECT:
                question_choices = q.get_choices()
                # add an empty option at the top so that the user has to
                # explicitly select one of the options
                question_choices = tuple([('', '-------------')]) + question_choices
                self.fields["question_%d" % q.pk] = forms.ChoiceField(label=q.text,
                                                                      widget=forms.Select,
                                                                      choices=question_choices)
                try:
                    if response:
                        initial = AnswerSelect.objects.get(id=response.id)
                        self.fields["question_%d" % q.pk].initial = initial.body
                except Exception as e:
                    logging.exception("Exception in response form - AnswerSelect: %s", e)

            elif q.question_type == Question.SELECT_MULTIPLE:
                question_choices = q.get_choices()
                self.fields["question_%d" % q.pk] = forms.\
                    MultipleChoiceField(label=q.text,
                                        widget=forms.CheckboxSelectMultiple,
                                        choices=question_choices)
                try:
                    if response:
                        initial = AnswerSelectMultiple.objects.get(id=response.id)
                        self.fields["question_%d" % q.pk].initial = initial.body
                except Exception as e:
                    logging.exception("Exception in response form - AnswerSelectMultiple %s", e)

            elif q.question_type == Question.INTEGER:
                self.fields["question_%d" % q.pk] = forms.IntegerField(label=q.text)
                try:
                    if response:
                        initial = AnswerInteger.objects.get(id=response.id)
                        self.fields["question_%d" % q.pk].initial = initial.body
                except Exception as e:
                    logging.exception("Exception in response form - AnswerInteger %s", e)

            # if the field is required, give it a corresponding css class.
            if q.required:
                self.fields["question_%d" % q.pk].required = True
                self.fields["question_%d" % q.pk].widget.attrs["class"] = "required"
            else:
                self.fields["question_%d" % q.pk].required = False

            # add the category as a css class, and add it as a data attribute
            # as well (this is used in the template to allow sorting the questions by category)
            if q.category:
                classes = self.fields["question_%d" % q.pk].widget.attrs.get("class")
                if classes:
                    self.fields["question_%d" % q.pk].widget.attrs["class"] \
                        = classes + (" cat_%s" % q.category.name)
                else:
                    self.fields["question_%d" % q.pk].widget.attrs["class"] \
                        = (" cat_%s" % q.category.name)
                self.fields["question_%d" % q.pk].widget.attrs["category"] = q.category.name

            # initialize the form field with values from a POST request, if any.

    def save(self, commit=True):
        # save the response object
        response = super(ResponseForm, self).save(commit=False)
        response.user = self.user
        response.survey = self.survey
        response.interview_uuid = self.uuid
        response.is_finished = self.is_finished
        response.save()

        # create an answer object for each question and associate it with this
        # response.
        for field_name, field_value in self.cleaned_data.items():
            if field_name.startswith("question_"):
                # warning: this way of extracting the id is very fragile and
                # entirely dependent on the way the question_id is encoded in the
                # field name in the __init__ method of this form class.
                q_id = int(field_name.split("_")[1])
                q = Question.objects.get(pk=q_id)

                if q.question_type == Question.TEXT:
                    a = AnswerText(question=q)
                    a.body = field_value
                elif q.question_type == Question.RADIO:
                    a = AnswerRadio(question=q)
                    a.body = field_value
                elif q.question_type == Question.SELECT:
                    a = AnswerSelect(question=q)
                    a.body = field_value
                elif q.question_type == Question.SELECT_MULTIPLE:
                    a = AnswerSelectMultiple(question=q)
                    a.body = field_value
                elif q.question_type == Question.INTEGER:
                    a = AnswerInteger(question=q)
                    a.body = field_value

                a.response = response
                if response:
                    try:
                        ab = AnswerBase.objects.get(response=response, question=q)
                        if ab:
                            a.id = ab.id
                            a.created = ab.created
                            a.updated = ab.updated
                            a.save()
                        else:
                            a.save()
                    except Exception as e:
                        logging.exception("Exception in save response form %s", e)
                        a.save()
        return response
