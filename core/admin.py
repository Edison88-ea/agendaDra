from django.contrib import admin
from .models import Paciente, Clinica, Dentista, Consulta

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'cpf')
    search_fields = ('nome', 'cpf', 'exames') # Adicionado 'exames' para pesquisa
    fields = ('nome', 'telefone', 'email', 'data_nascimento', 'cpf', 'exames') # Adicionado 'exames' para edição

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
    list_display = ('paciente', 'clinica', 'data_hora', 'status', 'valor', 'pago')
    list_filter = ('clinica', 'data_hora', 'status', 'pago')
    search_fields = ('paciente__nome', 'procedimento')
    date_hierarchy = 'data_hora'
    fields = ('paciente', 'dentista', 'clinica', 'data_hora', 'procedimento', 'valor', 'pago','status', 'observacoes')
    list_editable = ('status', 'pago')