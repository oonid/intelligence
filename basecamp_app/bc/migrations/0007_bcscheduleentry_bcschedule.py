# Generated by Django 4.2.6 on 2023-11-22 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('bc', '0006_bcquestionnaire_bcquestion_bcquestionanswer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BcScheduleEntry',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=30)),
                ('visible_to_clients', models.BooleanField()),
                ('created_at', models.DateTimeField(db_index=True)),
                ('updated_at', models.DateTimeField()),
                ('title', models.CharField(max_length=100)),
                ('inherits_status', models.BooleanField()),
                ('type', models.CharField(max_length=30)),
                ('url', models.URLField()),
                ('app_url', models.URLField()),
                ('bookmark_url', models.URLField()),
                ('subscription_url', models.URLField()),
                ('comments_count', models.IntegerField()),
                ('comments_url', models.URLField()),
                ('object_id', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=100)),
                ('summary', models.CharField(max_length=100)),
                ('all_day', models.BooleanField()),
                ('starts_at', models.DateTimeField()),
                ('ends_at', models.DateTimeField()),
                ('bucket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bc.bcproject')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bc.bcpeople')),
                ('participants', models.ManyToManyField(related_name='schedule_entry_participants', to='bc.bcpeople')),
                ('recurrence_schedule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bc.bcrecurrenceschedule')),
            ],
        ),
        migrations.CreateModel(
            name='BcSchedule',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=30)),
                ('visible_to_clients', models.BooleanField()),
                ('created_at', models.DateTimeField(db_index=True)),
                ('updated_at', models.DateTimeField()),
                ('title', models.CharField(max_length=100)),
                ('inherits_status', models.BooleanField()),
                ('type', models.CharField(max_length=30)),
                ('url', models.URLField()),
                ('app_url', models.URLField()),
                ('bookmark_url', models.URLField()),
                ('position', models.IntegerField(null=True)),
                ('include_due_assignments', models.BooleanField()),
                ('entries_count', models.IntegerField()),
                ('entries_url', models.URLField()),
                ('bucket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bc.bcproject')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bc.bcpeople')),
            ],
        ),
    ]
