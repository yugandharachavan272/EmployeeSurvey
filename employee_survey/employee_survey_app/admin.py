from django.contrib import admin
from .models import UserProfileInfo, User, Organisation, Question, Category, Survey, UsersSurveys, Response, AnswerText, AnswerRadio, AnswerSelect, AnswerInteger, AnswerSelectMultiple
from employee_survey_app import EmailModel

# Register your models here.
admin.site.register(UserProfileInfo)
admin.site.register(Organisation)


class QuestionInline(admin.TabularInline):
    model = Question
    ordering = ('category',)
    extra = 0


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class SurveyAdmin(admin.ModelAdmin):
    inlines = [CategoryInline, QuestionInline]


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


class UsersSurveysAdmin(admin.ModelAdmin):
    # FILTER USER AND SHOW EMPLOYES OF HIS ORGANISATION
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        user_profile = UserProfileInfo.objects.filter(user_id=request.user.id)
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(userprofileinfo__organisation_id=user_profile[0].organisation_id)
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


# admin.site.register(Question, QuestionInline)
# admin.site.register(Category, CategoryInline)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(UsersSurveys, UsersSurveysAdmin)
admin.site.register(Response, ResponseAdmin)

