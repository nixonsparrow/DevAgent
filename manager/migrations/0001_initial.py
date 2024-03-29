# Generated by Django 3.2.19 on 2024-02-23 17:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='name')),
                ('location', models.CharField(blank=True, max_length=32, null=True, verbose_name='location')),
                ('website', models.CharField(blank=True, max_length=64, null=True, verbose_name='website')),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='companies_added', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'company',
                'verbose_name_plural': 'companies',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=64, verbose_name='title')),
                ('status', models.SmallIntegerField(choices=[(0, 'Created'), (1, 'Application sent'), (2, 'Active'), (3, 'Positive response'), (4, 'Contract signed'), (-1, 'Negative response'), (-2, 'Resigned')], default=0, verbose_name='status')),
                ('employment_type', models.CharField(choices=[('None', 'None'), ('B2B', 'Business to business'), ('PERMANENT', 'Permanent'), ('CONTRACT', 'Contract')], default='None', max_length=16, null=True, verbose_name='employment type')),
                ('level', models.PositiveSmallIntegerField(choices=[(0, 'Not provided'), (1, 'Junior'), (2, 'Regular'), (3, 'Senior')], default=0, verbose_name='experience level')),
                ('earnings_min', models.PositiveSmallIntegerField(blank=True, default=None, null=True, verbose_name='earnings min')),
                ('earnings_max', models.PositiveSmallIntegerField(blank=True, default=None, null=True, verbose_name='earnings max')),
                ('currency', models.CharField(blank=True, default='PLN', max_length=8, null=True, verbose_name='currency')),
                ('application_sent_on', models.DateTimeField(blank=True, default=None, null=True, verbose_name='application sent date and time')),
                ('remote', models.BooleanField(default=True, verbose_name='remote')),
                ('location', models.CharField(blank=True, max_length=32, null=True, verbose_name='location')),
                ('description', models.TextField(blank=True, max_length=2048, null=True, verbose_name='description')),
                ('comments', models.TextField(blank=True, max_length=512, null=True, verbose_name='comments')),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.company')),
                ('developer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'offer',
                'verbose_name_plural': 'offers',
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='name')),
            ],
            options={
                'verbose_name': 'skill',
                'verbose_name_plural': 'skills',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='StepType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='step_types_added', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecruitmentStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True, max_length=2048, null=True, verbose_name='description')),
                ('status', models.SmallIntegerField(choices=[(0, 'Created'), (1, 'Planned'), (2, 'Waiting for response'), (3, 'Positive response'), (-1, 'Negative response'), (-2, 'Resigned')], default=0, verbose_name='status')),
                ('scheduled_on', models.DateTimeField(blank=True, null=True, verbose_name='scheduled on')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='manager.offer')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.steptype')),
            ],
            options={
                'verbose_name': 'recruitment step',
                'verbose_name_plural': 'recruitment steps',
                'ordering': ['-updated_on', '-created_on'],
            },
        ),
        migrations.AddField(
            model_name='offer',
            name='skills_optional',
            field=models.ManyToManyField(blank=True, related_name='offers_optional_in', to='manager.Skill', verbose_name='skills optional'),
        ),
        migrations.AddField(
            model_name='offer',
            name='skills_required',
            field=models.ManyToManyField(related_name='offers_required_in', to='manager.Skill', verbose_name='skills required'),
        ),
    ]
