"""Umbral de espacio libre configurable y camaras asociadas a pasillo y gondola
con su calibracion de lente (CU05, item #44)."""

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_ubicacion_y_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('umbral', models.PositiveSmallIntegerField(default=30, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='umbral de espacio libre (%)')),
            ],
        ),
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=60, unique=True)),
                ('pasillo', models.CharField(max_length=20)),
                ('gondola', models.CharField(max_length=20, verbose_name='góndola')),
                ('calibracion', models.JSONField(blank=True, null=True, verbose_name='calibración de lente')),
            ],
            options={
                'ordering': ['pasillo', 'gondola'],
                'constraints': [models.UniqueConstraint(fields=('pasillo', 'gondola'), name='una_camara_por_gondola', violation_error_message='Esa góndola ya tiene una cámara.')],
            },
        ),
    ]
