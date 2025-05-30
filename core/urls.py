from django.urls import path
from .views import (
    AgendaView, AgendarConsultaCreateView, ConsultaUpdateView, ConsultaDeleteView,
    PacienteListView, PacienteCreateView, PacienteUpdateView, PacienteDeleteView,
    ClinicaListView, ClinicaCreateView, ClinicaUpdateView, ClinicaDeleteView,
    get_consultas_json,
    relatorio_financeiro,
    ExcluirExameConsultaArquivoView,
    ExcluirTermoConsultaArquivoView,
    ExcluirExamePacienteArquivoView,
    ExcluirTermoPacienteArquivoView,
)

urlpatterns = [
    path('', AgendaView.as_view(), name='agenda'),
    path('agendar/', AgendarConsultaCreateView.as_view(), name='agendar_consulta'),
    path('consulta/<int:pk>/editar/', ConsultaUpdateView.as_view(), name='editar_consulta'),
    path('consulta/<int:pk>/excluir/', ConsultaDeleteView.as_view(), name='excluir_consulta'),

   
    path('exame-consulta-arquivo/<int:pk>/excluir/', ExcluirExameConsultaArquivoView.as_view(), name='excluir_exame_consulta_arquivo'),
    path('termo-consulta-arquivo/<int:pk>/excluir/', ExcluirTermoConsultaArquivoView.as_view(), name='excluir_termo_consulta_arquivo'),

    path('pacientes/', PacienteListView.as_view(), name='paciente_list'),
    path('pacientes/novo/', PacienteCreateView.as_view(), name='novo_paciente'),
    path('pacientes/<int:pk>/editar/', PacienteUpdateView.as_view(), name='editar_paciente'),
    path('pacientes/<int:pk>/excluir/', PacienteDeleteView.as_view(), name='excluir_paciente'),
    
    
    path('paciente-exame-arquivo/<int:pk>/excluir/', ExcluirExamePacienteArquivoView.as_view(), name='excluir_exame_paciente_arquivo'),
    path('paciente-termo-arquivo/<int:pk>/excluir/', ExcluirTermoPacienteArquivoView.as_view(), name='excluir_termo_paciente_arquivo'),

    path('clinicas/', ClinicaListView.as_view(), name='clinica_list'),
    path('clinicas/novo/', ClinicaCreateView.as_view(), name='nova_clinica'),
    path('clinicas/<int:pk>/editar/', ClinicaUpdateView.as_view(), name='editar_clinica'),
    path('clinicas/<int:pk>/excluir/', ClinicaDeleteView.as_view(), name='excluir_clinica'),

    path('api/consultas/', get_consultas_json, name='api_consultas_json'),
    path('relatorio/financeiro/', relatorio_financeiro, name='relatorio_financeiro'),
]
