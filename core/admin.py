from django.contrib import admin
from .models import Paciente, Clinica, Dentista, Consulta

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'cpf')
    search_fields = ('nome', 'cpf', 'exames')
    fields = ('nome', 'telefone', 'email', 'data_nascimento', 'cpf', 'exames', 'arquivo_exame_paciente', 'termo_paciente')

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
    # Alterado 'data_hora' para 'data_consulta' e 'hora_inicio'
    list_display = ('paciente', 'clinica', 'data_consulta', 'hora_inicio', 'hora_fim', 'status', 'pago', 'valor')
    # Alterado 'data_hora' para 'data_consulta'
    list_filter = ('clinica', 'data_consulta', 'status', 'pago')
    search_fields = ('paciente__nome', 'procedimento')
    # Alterado 'data_hora' para 'data_consulta'
    date_hierarchy = 'data_consulta' # Usar data_consulta para hierarquia de data
    
    # Campos que podem ser editados diretamente na lista do admin
    list_editable = ('status', 'pago') 

    # Campos exibidos no formulário de edição/criação
    fields = ('paciente', 'dentista', 'clinica', 'data_consulta', 'hora_inicio', 'hora_fim', 'procedimento', 'valor', 'pago', 'status', 'observacoes', 'arquivo_exame')



