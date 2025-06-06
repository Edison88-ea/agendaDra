# Generated by Django 5.2.1 on 2025-06-04 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_consulta_arquivo_exame_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='consulta',
            options={'ordering': ['data_consulta', 'hora_inicio'], 'permissions': [('can_add_consulta_files', 'Can add consultation files (exams and terms)'), ('view_relatorio_financeiro', 'Can view financial report')]},
        ),
        migrations.AlterModelOptions(
            name='paciente',
            options={'permissions': [('can_add_paciente_files', 'Can add patient files (exams and terms)')]},
        ),
    ]
