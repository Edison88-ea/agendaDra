# Generated by Django 5.2.1 on 2025-05-29 23:35

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
            name='Clinica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('endereco', models.CharField(max_length=200)),
                ('telefone', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('telefone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('data_nascimento', models.DateField(blank=True, null=True)),
                ('cpf', models.CharField(blank=True, max_length=14, null=True, unique=True)),
                ('arquivo_exame_paciente', models.FileField(blank=True, null=True, upload_to='pacientes_exames/')),
                ('termo_paciente', models.FileField(blank=True, null=True, upload_to='termos_pacientes/')),
            ],
        ),
        migrations.CreateModel(
            name='Dentista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cro', models.CharField(max_length=20, unique=True)),
                ('nome_completo', models.CharField(max_length=100)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Consulta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_consulta', models.DateField(verbose_name='Data da Consulta')),
                ('hora_inicio', models.TimeField(verbose_name='Horário de Início')),
                ('hora_fim', models.TimeField(verbose_name='Horário de Fim')),
                ('procedimento', models.CharField(blank=True, max_length=200, null=True)),
                ('valor', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('pago', models.BooleanField(default=False)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('AGENDADO', 'Agendado'), ('CONFIRMADO', 'Confirmado'), ('ATENDIDO', 'Atendido'), ('CANCELADO', 'Cancelado'), ('NAO_COMPARECEU', 'Não Compareceu'), ('RESERVADO', 'Reservado')], default='AGENDADO', max_length=20)),
                ('arquivo_exame', models.FileField(blank=True, null=True, upload_to='exames/')),
                ('clinica', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.clinica')),
                ('dentista', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.dentista')),
                ('paciente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.paciente')),
            ],
            options={
                'ordering': ['data_consulta', 'hora_inicio'],
            },
        ),
    ]
