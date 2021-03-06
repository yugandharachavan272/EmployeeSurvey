# Generated by Django 2.1.5 on 2019-03-27 06:41

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee_survey_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.RemoveField(
            model_name='userssurveys',
            name='survey',
        ),
        migrations.RemoveField(
            model_name='userssurveys',
            name='user',
        ),
        migrations.RemoveField(
            model_name='category',
            name='survey',
        ),
        migrations.RemoveField(
            model_name='question',
            name='category',
        ),
        migrations.RemoveField(
            model_name='question',
            name='survey',
        ),
        migrations.AddField(
            model_name='organisation',
            name='is_archived',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='questions',
            field=models.ManyToManyField(to='employee_survey_app.Question'),
        ),
        migrations.AlterField(
            model_name='user',
            name='organisation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='organisations', to='employee_survey_app.Organisation'),
        ),
        migrations.DeleteModel(
            name='UsersSurveys',
        ),
        migrations.AddField(
            model_name='surveyuser',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee_survey_app.Survey'),
        ),
        migrations.AddField(
            model_name='surveyuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='response',
            name='survey_user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employee_survey_app.SurveyUser'),
        ),
        migrations.AddField(
            model_name='survey',
            name='user',
            field=models.ManyToManyField(through='employee_survey_app.SurveyUser', to=settings.AUTH_USER_MODEL),
        ),
    ]
