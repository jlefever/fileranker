# Generated by Django 5.0.6 on 2024-07-01 02:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.TextField()),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(choices=[('A', 'Prefer A'), ('B', 'Prefer B'), ('U', 'Unsure')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Sequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('seed', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SequenceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField()),
            ],
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.UniqueConstraint(fields=('name',), name='unique_project_name'),
        ),
        migrations.AddField(
            model_name='file',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='filerater.project'),
        ),
        migrations.AddField(
            model_name='response',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='sequence',
            constraint=models.UniqueConstraint(fields=('name',), name='unique_sequence_name'),
        ),
        migrations.AddField(
            model_name='sequenceitem',
            name='file_a',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='filerater.file'),
        ),
        migrations.AddField(
            model_name='sequenceitem',
            name='file_b',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='filerater.file'),
        ),
        migrations.AddField(
            model_name='sequenceitem',
            name='sequence',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='filerater.sequence'),
        ),
        migrations.AddField(
            model_name='response',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='filerater.sequenceitem'),
        ),
        migrations.AddConstraint(
            model_name='file',
            constraint=models.UniqueConstraint(fields=('project', 'filename'), name='unique_filename_per_project'),
        ),
        migrations.AddConstraint(
            model_name='sequenceitem',
            constraint=models.UniqueConstraint(fields=('sequence', 'position'), name='unique_position_per_sequence'),
        ),
        migrations.AddConstraint(
            model_name='sequenceitem',
            constraint=models.UniqueConstraint(fields=('sequence', 'file_a', 'file_b'), name='unique_files_per_sequence'),
        ),
        migrations.AddConstraint(
            model_name='sequenceitem',
            constraint=models.CheckConstraint(check=models.Q(('file_a_id__lt', models.F('file_b_id'))), name='item_a_lt_b'),
        ),
        migrations.AddConstraint(
            model_name='response',
            constraint=models.UniqueConstraint(fields=('user', 'item'), name='unique_response'),
        ),
    ]
