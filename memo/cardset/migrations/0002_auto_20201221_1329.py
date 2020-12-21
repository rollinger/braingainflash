# Generated by Django 3.0.11 on 2020-12-21 12:29

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('cardset', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='memocard',
            name='unique_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='memoset',
            name='unique_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='memocard',
            name='memoset',
            field=models.ForeignKey(help_text='Memo Card is assigned to this set', on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='cardset.MemoSet'),
        ),
    ]