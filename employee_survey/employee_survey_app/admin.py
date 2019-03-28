# pylint: disable=invalid-name
# pylint: disable=broad-except
# pylint: disable=missing-docstring
# pylint: disable=no-member
"""
Register created module here
"""
import logging
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.db import IntegrityError
from .models import User, Organisation, Question, Category, SurveyUser, Survey, Response, \
    AnswerText, AnswerRadio, AnswerSelect, AnswerInteger, AnswerSelectMultiple

# Register your models here.
admin.site.register(Organisation)


class UserResource(resources.ModelResource):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring, too-few-public-methods
        model = User
        import_id_fields = ('username',)
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UserResource, self).__init__(*args, **kwargs)

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        try:
            organisation_id = self.request.user.organisation_id
            logged_user_password = self.request.user.password
            self.request.user.set_password(instance.password)
            instance.password = self.request.user.password
            self.request.user.password = logged_user_password
            if organisation_id > 0:
                try:
                    instance.organisation_id = organisation_id
                except Exception as e:  # pylint: disable=invalid-name
                    logging.exception("Exception in UserResource save in try %s", e)
            super(UserResource, self).save_instance(instance, using_transactions, dry_run)
        except IntegrityError:
            logging.exception("Exception in UserResource save %s", IntegrityError)


class UserAdmin(ImportExportModelAdmin):  # pylint: disable=too-many-ancestors,missing-docstring
    resource_class = UserResource

    def get_resource_kwargs(self, request, *args, **kwargs):
        """ Passing request to resource obj to control exported fields dynamically """
        return {'request': request}

    def get_queryset(self, request):
        qs = super().get_queryset(request)  # pylint: disable=invalid-name
        if request.user.is_superuser:
            return qs
        if request.user.groups.filter(name='SuperAdmin').exists():
            return qs
        return qs.filter(organisation_id=request.user.organisation_id)

    # FILTER USER AND SHOW EMPLOYEES OF HIS ORGANISATION
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organisation_id":
            if request.user.is_staff and not request.user.is_superuser:
                if request.user.groups.filter(name='OrganisationAdmin').exists():
                    kwargs["queryset"] = Organisation.objects.\
                        filter(organisation_id=request.user.organisation_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# class QuestionInline(admin.TabularInline):  # pylint: disable=missing-docstring
#     model = Question
#     ordering = ('category',)
#     extra = 0
#
#
# class CategoryInline(admin.TabularInline):  # pylint: disable=missing-docstring
#     model = Category
#     extra = 0

class SurveyQuestionsInline(admin.TabularInline):
    #     # model = SurveyQuestions
    #     # extra = 1
    model = Survey.questions.through
    verbose_name = u"Question"
    verbose_name_plural = u"Questions",
    # raw_id_fields = ("question",)
    extra = 1


class UsersSurveysInline(admin.TabularInline):  # pylint: disable=missing-docstring
    # model = SurveyUser
    model = Survey.user.through
    # verbose_name = "User",
    # verbose_name_plural = "Users",
    # raw_id_fields = ('user',)
    extra = 1
    # filter_horizontal = ('user',)

    def get_field_queryset(self, db, db_field, request):
        qs = super().get_field_queryset(db, db_field, request)
        if qs:
            if request.user.is_superuser:
                return qs
            if db_field.name == 'user':
                return qs.filter(organisation=request.user.organisation_id)
        return qs

    def get_queryset(self, request):
        qs = super(UsersSurveysInline, self).get_queryset(request)
        if not request.user.is_superuser:
            print(" qs ", qs)
            return qs.filter(user_id__in=User.objects.
                             filter(organisation_id=request.user.organisation_id))
        return qs


class SurveyAdmin(admin.ModelAdmin):  # pylint: disable=missing-docstring
    filter_horizontal = ("questions",)
    inlines = (UsersSurveysInline, )
    # exclude = ("questions",)


class AnswerBaseInline(admin.StackedInline):  # pylint: disable=missing-docstring
    fields = ('question', 'body')
    readonly_fields = ('question',)
    extra = 0


class AnswerTextInline(AnswerBaseInline):  # pylint: disable=missing-docstring
    model = AnswerText


class AnswerRadioInline(AnswerBaseInline):  # pylint: disable=missing-docstring
    model = AnswerRadio


class AnswerSelectInline(AnswerBaseInline):  # pylint: disable=missing-docstring
    model = AnswerSelect


class AnswerSelectMultipleInline(AnswerBaseInline):  # pylint: disable=missing-docstring
    model = AnswerSelectMultiple


class AnswerIntegerInline(AnswerBaseInline):  # pylint: disable=missing-docstring
    model = AnswerInteger


class ResponseAdmin(admin.ModelAdmin):  # pylint: disable=missing-docstring
    list_display = ('interview_uuid', 'user', 'created')
    inlines = [AnswerTextInline, AnswerRadioInline, AnswerSelectInline,
               AnswerSelectMultipleInline, AnswerIntegerInline]
    # specifies the order as well as which fields to act on
    readonly_fields = ('survey', 'created', 'updated', 'interview_uuid')

    # FILTER USER AND SHOW EMPLOYEES OF HIS ORGANISATION
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            if request.user.is_staff and not request.user.is_superuser:
                if request.user.groups.filter(name='OrganisationAdmin').exists():
                    kwargs["queryset"] = User.objects.\
                        filter(organisation_id=request.user.organisation_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question)
admin.site.register(Response, ResponseAdmin)
admin.site.register(User, UserAdmin)
