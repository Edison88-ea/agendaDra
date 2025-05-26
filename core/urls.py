from django.conf import settings # Importe settings
from django.conf.urls.static import static # Importe static
from django.urls import path
from .views import (
    AgendaView, AgendarConsultaCreateView, ConsultaUpdateView, ConsultaDeleteView,
    PacienteListView, PacienteCreateView, PacienteUpdateView,
    ClinicaListView, ClinicaCreateView, ClinicaUpdateView,
    get_consultas_json, # <--- Certifique-se de que 'get_consultas_json' está importado aqui!
    relatorio_financeiro # <--- E também o 'relatorio_financeiro'
)

urlpatterns = [
    path('', AgendaView.as_view(), name='agenda'),
    path('agendar/', AgendarConsultaCreateView.as_view(), name='agendar_consulta'),
    path('consulta/<int:pk>/editar/', ConsultaUpdateView.as_view(), name='editar_consulta'),
    path('consulta/<int:pk>/excluir/', ConsultaDeleteView.as_view(), name='excluir_consulta'),

    path('pacientes/', PacienteListView.as_view(), name='paciente_list'),
    path('pacientes/novo/', PacienteCreateView.as_view(), name='novo_paciente'),
    path('pacientes/<int:pk>/editar/', PacienteUpdateView.as_view(), name='editar_paciente'),

    path('clinicas/', ClinicaListView.as_view(), name='clinica_list'),
    path('clinicas/novo/', ClinicaCreateView.as_view(), name='nova_clinica'),
    path('clinicas/<int:pk>/editar/', ClinicaUpdateView.as_view(), name='editar_clinica'),

    # <--- ESTA LINHA É CRÍTICA! Certifique-se de que ela está presente e correta.
    path('api/consultas/', get_consultas_json, name='api_consultas_json'),
    
    # <--- E esta linha para o relatório financeiro
    path('relatorio/financeiro/', relatorio_financeiro, name='relatorio_financeiro'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
