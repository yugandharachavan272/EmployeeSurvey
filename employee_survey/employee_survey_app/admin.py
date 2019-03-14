import logging
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.db import IntegrityError
from .models import User, Organisation, Question, Category, SurveyUser, Survey, Response, AnswerText, AnswerRadio, \
    AnswerSelect, AnswerInteger, AnswerSelectMultiple

# Register your models here.
admin.site.register(Organisation)


class UserResource(resources.ModelResource):
    class Meta:
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
                except Exception as e:
                    logging.exception("Exception in UserResource save in try", e)
            super(UserResource, self).save_instance(instance, using_transactions, dry_run)
        except IntegrityError:
            logging.exception("Exception in UserResource save", IntegrityError)


class UserAdmin(ImportExportModelAdmin):
    resource_class = UserResource

    def get_resource_kwargs(self, request, *args, **kwargs):
        """ Passing request to resource obj to control exported fields dynamically """
        return {'request': request}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
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
                    kwargs["queryset"] = Organisation.objects.filter(organisation_id=request.user.organisation_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class QuestionInline(admin.TabularInline):
    model = Question
    ordering = ('category',)
    extra = 0


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class UsersSurveysInline(admin.TabularInline):
    model = SurveyUser
    extra = 1

    def get_field_queryset(self, db, db_field, request):
        qs = super().get_field_queryset(db, db_field, request)
        if request.user.is_superuser:
            return qs
        if db_field.name == 'user':
            return qs.filter(organisation=request.user.organisation_id)
        return qs

    def get_queryset(self, request):
        qs = super(UsersSurveysInline, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(user_id__in=User.objects.filter(organisation_id=request.user.organisation_id))
        return qs


class SurveyAdmin(admin.ModelAdmin):
    inlines = [CategoryInline, QuestionInline, UsersSurveysInline]


class AnswerBaseInline(admin.StackedInline):
    fields = ('question', 'body')
    readonly_fields = ('question',)
    extra = 0


class AnswerTextInline(AnswerBaseInline):
    model = AnswerText


class AnswerRadioInline(AnswerBaseInline):
    model = AnswerRadio


class AnswerSelectInline(AnswerBaseInline):
    model = AnswerSelect


class AnswerSelectMultipleInline(AnswerBaseInline):
    model = AnswerSelectMultiple


class AnswerIntegerInline(AnswerBaseInline):
    model = AnswerInteger


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('interview_uuid', 'user', 'created')
    inlines = [AnswerTextInline, AnswerRadioInline, AnswerSelectInline, AnswerSelectMultipleInline, AnswerIntegerInline]
    # specifies the order as well as which fields to act on
    readonly_fields = ('survey', 'created', 'updated', 'interview_uuid')

    # FILTER USER AND SHOW EMPLOYEES OF HIS ORGANISATION
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            if request.user.is_staff and not request.user.is_superuser:
                if request.user.groups.filter(name='OrganisationAdmin').exists():
                    kwargs["queryset"] = User.objects.filter(organisation_id=request.user.organisation_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(User, UserAdmin)

