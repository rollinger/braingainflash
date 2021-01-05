# Generated by Django 3.0.11 on 2021-01-02 09:21

import ckeditor.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('studygroups', '0010_auto_20210102_0627'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('title', models.CharField(help_text='Title of Topic', max_length=255, verbose_name='Title')),
                ('group', models.ForeignKey(help_text='Study group of the topic', on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='studygroups.StudyGroup')),
            ],
            options={
                'verbose_name': 'Topic',
                'verbose_name_plural': 'Topics',
                'ordering': ('group', 'title'),
                'unique_together': {('group', 'title')},
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('front_text', ckeditor.fields.RichTextField(help_text='Usually the Question', max_length=2000, verbose_name='Frontside Text')),
                ('back_text', ckeditor.fields.RichTextField(help_text='Usually the Question', max_length=2000, verbose_name='Backside Text')),
                ('creator', models.ForeignKey(help_text='Card is created by this user', on_delete=django.db.models.deletion.CASCADE, related_name='cards', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(help_text='Card is assigned to this group', on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='studygroups.StudyGroup')),
                ('topic', models.ForeignKey(blank=True, help_text='Card is grouped by this topic (optional)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='flashcards.Topic')),
            ],
            options={
                'verbose_name': 'Card',
                'verbose_name_plural': 'Cards',
                'ordering': ('group', '-topic', 'front_text'),
                'unique_together': {('group', 'front_text')},
            },
        ),
        migrations.CreateModel(
            name='Performance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('learn_timeout', models.PositiveSmallIntegerField(default=120, help_text='Timeout in seconds for learning the card', verbose_name='Learning Timeout')),
                ('recall_timeout', models.PositiveSmallIntegerField(default=120, help_text='Timeout in seconds for recalling the card', verbose_name='Recalling Timeout')),
                ('is_paused', models.BooleanField(default=False, help_text='Learning of associated card is paused.', verbose_name='Paused')),
                ('priority', models.CharField(choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High')], default='normal', help_text='Default role of new member', max_length=20, verbose_name='Learning Priority')),
                ('data', jsonfield.fields.JSONField(default={'learning': [], 'recalling': []}, verbose_name='Performance Data')),
                ('recall_total_time', models.PositiveIntegerField(default=0, help_text='Total time spend on testing', verbose_name='Total Recall Time')),
                ('recall_trials', models.PositiveIntegerField(default=0, help_text='Total recalls tried', verbose_name='Total Recall Trials')),
                ('recall_score', models.DecimalField(decimal_places=1, default=0.0, help_text='Recall Score of the Card for the User', max_digits=4, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)], verbose_name='Recall Score')),
                ('learn_total_time', models.PositiveIntegerField(default=0, help_text='Total time spend on learning', verbose_name='Total Learn Time')),
                ('learn_trials', models.PositiveIntegerField(default=0, help_text='Total learnings tried', verbose_name='Total Learn Trials')),
                ('learn_score', models.DecimalField(decimal_places=1, default=0.0, help_text='Learn Score of the Card for the User', max_digits=4, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)], verbose_name='Learn Score')),
                ('card', models.ForeignKey(help_text='Card of the performance', on_delete=django.db.models.deletion.CASCADE, related_name='memo_performances', to='flashcards.Card')),
                ('owner', models.ForeignKey(help_text='User of the card performance', on_delete=django.db.models.deletion.CASCADE, related_name='memo_performances', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Performance',
                'verbose_name_plural': 'Performances',
                'ordering': ('owner', '-recall_score'),
                'unique_together': {('owner', 'card')},
            },
        ),
    ]