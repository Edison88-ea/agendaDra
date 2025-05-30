from django.contrib import admin
from .models import Paciente, Clinica, Consulta, Dentista, TermoPacienteArquivo, ExamePacienteArquivo, ExameConsultaArquivo, TermoConsultaArquivo # Importar novos modelos

# Inline para Exames do Paciente
class ExamePacienteArquivoInline(admin.TabularInline):
    model = ExamePacienteArquivo
    extra = 1
    fields = ['arquivo', 'descricao']

# Inline para Termos do Paciente
class TermoPacienteArquivoInline(admin.TabularInline):
    model = TermoPacienteArquivo
    extra = 1
    fields = ['arquivo', 'descricao']

# NOVOS Inlines para Consulta
class ExameConsultaArquivoInline(admin.TabularInline):
    model = ExameConsultaArquivo
    extra = 1
    fields = ['arquivo', 'descricao']

class TermoConsultaArquivoInline(admin.TabularInline):
    model = TermoConsultaArquivo
    extra = 1
    fields = ['arquivo', 'descricao']

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'cpf', 'clinica_principal')
    search_fields = ('nome', 'cpf', 'email', 'clinica_principal__nome')
    fields = ('nome', 'telefone', 'email', 'data_nascimento', 'cpf', 'clinica_principal') 
    inlines = [ExamePacienteArquivoInline, TermoPacienteArquivoInline]

@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco', 'telefone')
    search_fields = ('nome',)

@admin.register(Dentista)
class DentistaAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cro')
    search_fields = ('nome_completo', 'cro')

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'clinica', 'data_consulta', 'hora_inicio', 'hora_fim', 'status', 'pago', 'valor')
    list_filter = ('clinica', 'data_consulta', 'status', 'pago')
    search_fields = ('paciente__nome', 'procedimento')
    date_hierarchy = 'data_consulta'
    list_editable = ('status', 'pago') 
    # Removido 'arquivo_exame' dos fields
    fields = ('paciente', 'dentista', 'clinica', 'data_consulta', 'hora_inicio', 'hora_fim', 'procedimento', 'valor', 'pago', 'status', 'observacoes')
    inlines = [ExameConsultaArquivoInline, TermoConsultaArquivoInline] # Adiciona ambos os inlines da consulta
