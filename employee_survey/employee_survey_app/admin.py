from django.contrib import admin
from .models import User, Organisation, Question, Category, SurveyUser, Survey, Response, AnswerText, AnswerRadio, AnswerSelect, AnswerInteger, AnswerSelectMultiple
from employee_survey_app import EmailModel
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin
from import_export import resources, widgets
from import_export.admin import ImportExportModelAdmin
from django.db import IntegrityError
from django.contrib.auth.models import User as AuthUser
# Register your models here.
# admin.site.register(UserProfileInfo)
admin.site.register(Organisation)


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        import_id_fields = ('username',)
        fields = ('username', 'password')
    '''
    def save_instance(self, instance, real_dry_run):
        print("i m in save_instance")
        if not real_dry_run:
            try:
                print(" instance ", instance)
                #  obj = YourModel.objects.get(some_val=instance.some_val)
                # extra logic if object already exist
            except Exception as e:
                print(" Exception ", e)
                # create new object
                # obj = YourModel(some_val=instance.some_val)
                # obj.save()'''

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UserResource, self).__init__(*args, **kwargs)

        '''def import_obj(self, obj, data, dry_run):
        """
        Traverses every field in this Resource and calls
        :meth:`~import_export.resources.Resource.import_field`.
        """
        for field in self.get_fields():
            if isinstance(field.widget, widgets.ManyToManyWidget):
                continue

            # find specific `field_name`
            # param of `data` is OrderDict
            if field.column_name == 'username':
                # data.update({'password': AuthUser.set_password(data.get('username'))})
                data.update({'username': data.get('username')})
            # checkout the changed object
            print(" obj ", obj)
            self.import_field(field, obj, data)'''

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
                    print("Exception in org ", e)
            super(UserResource, self).save_instance(instance, using_transactions, dry_run)
        except IntegrityError:
            print("i m in IntegrityError", IntegrityError)
            pass


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

    # FILTER USER AND SHOW EMPLOYES OF HIS ORGANISATION
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

    # FILTER USER AND SHOW EMPLOYES OF HIS ORGANISATION
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            if request.user.is_staff and not request.user.is_superuser:
                if request.user.groups.filter(name='OrganisationAdmin').exists():
                    kwargs["queryset"] = User.objects.filter(organisation_id=request.user.organisation_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


'''
class UsersSurveysAdmin(admin.ModelAdmin):
    # FILTER USER AND SHOW EMPLOYES OF HIS ORGANISATION
    def formfield_for_manytomany(self, db_field, request, **kwargs):
       
        # user_profile = UserProfileInfo.objects.filter(user_id=request.user.id)
        # if db_field.name == "user":
        #     kwargs["queryset"] = User.objects.filter(userprofileinfo__organisation_id=user_profile[0].organisation_id)
           
        # user_profile = UserProfileInfo.objects.filter(user_id=request.user.id)
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(organisation_id=request.user.organisation_id)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # print(" i m in save..")
        survey = form.cleaned_data['survey']
        # print(" survey.name ", survey.name)
        users = form.cleaned_data['user']
        super().save_model(request, obj, form, change)
        for user in users:
            # print(" user : ", user.username, " email : ", user.email)
            subject = "Regarding ", survey.name
            sms_text = "You have assigned new survey", survey.name
            email_to = [user.email]
            EmailModel.send_mail_fun(subject, sms_text, email_to)
'''


# admin.site.register(Question, QuestionInline)
# admin.site.register(Category, CategoryInline)
admin.site.register(Survey, SurveyAdmin)
# admin.site.register(UsersSurveys, UsersSurveysAdmin)
admin.site.register(Response, ResponseAdmin)
# admin.site.unregister(User)
admin.site.register(User, UserAdmin)

