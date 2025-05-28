from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta, date, time # Adicione 'time' aqui
from .models import Paciente, Clinica, Consulta, Dentista
from .forms import ConsultaForm
from django.http import JsonResponse
from django.conf import settings # Adicione esta importação
import os # Adicione esta importação
from django.db.models import Sum # Importe Sum para agregação
from django.db.models import Q # Importe Q

class AgendaView(ListView):
    model = Consulta
    template_name = 'core/agenda.html'
    context_object_name = 'consultas'

    def get_queryset(self):
        year_str = self.request.GET.get('year')
        month_str = self.request.GET.get('month')
        day_str = self.request.GET.get('day')

        if year_str and month_str and day_str:
            try:
                current_date = date(int(year_str), int(month_str), int(day_str))
                start_of_week = current_date - timedelta(days=current_date.weekday())
                end_of_week = start_of_week + timedelta(days=6)
            except ValueError:
                start_of_week = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
                end_of_week = start_of_week + timedelta(days=6)
        else:
            today = timezone.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
        
        return Consulta.objects.filter(data_consulta__gte=start_of_week, data_consulta__lte=end_of_week).order_by('data_consulta', 'hora_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        year_str = self.request.GET.get('year')
        month_str = self.request.GET.get('month')
        day_str = self.request.GET.get('day')

        if year_str and month_str and day_str:
            try:
                current_date = date(int(year_str), int(month_str), int(day_str))
            except ValueError:
                current_date = timezone.now().date()
        else:
            current_date = timezone.now().date()
            
        start_of_week = current_date - timedelta(days=current_date.weekday())
        dates_in_week = [start_of_week + timedelta(days=i) for i in range(7)]

        context['dates_in_week'] = dates_in_week
        
        consultas_por_data = {}
        for consulta in self.get_queryset():
            data_consulta_obj = consulta.data_consulta
            if data_consulta_obj not in consultas_por_data:
                consultas_por_data[data_consulta_obj] = []
            consultas_por_data[data_consulta_obj].append(consulta)
        context['consultas_por_data'] = consultas_por_data

        prev_week_start = start_of_week - timedelta(weeks=1)
        next_week_start = start_of_week + timedelta(weeks=1)
        context['prev_week_url'] = f"{reverse_lazy('agenda')}?year={prev_week_start.year}&month={prev_week_start.month}&day={prev_week_start.day}"
        context['next_week_url'] = f"{reverse_lazy('agenda')}?year={next_week_start.year}&month={next_week_start.month}&day={next_week_start.day}"
        
        return context

class AgendarConsultaCreateView(CreateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = 'core/agendar_consulta_form.html'
    success_url = reverse_lazy('agenda')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        initial_data = {}
        data_param = self.request.GET.get('data')
        hora_inicio_param = self.request.GET.get('hora_inicio')
        
        if data_param:
            try:
                initial_data['data_consulta'] = datetime.strptime(data_param, '%Y-%m-%d').date()
            except ValueError:
                pass
        if hora_inicio_param:
            try:
                initial_data['hora_inicio'] = datetime.strptime(hora_inicio_param, '%H:%M').time()
                # Sugerir hora_fim 30 minutos depois
                initial_data['hora_fim'] = (datetime.strptime(hora_inicio_param, '%H:%M') + timedelta(minutes=30)).time()
            except ValueError:
                pass
        
        if initial_data:
            kwargs['initial'] = initial_data
            
        return kwargs

class ConsultaUpdateView(UpdateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = 'core/agendar_consulta_form.html'
    success_url = reverse_lazy('agenda')

class ConsultaDeleteView(DeleteView):
    model = Consulta
    template_name = 'core/consulta_confirm_delete.html'
    success_url = reverse_lazy('agenda')

class PacienteListView(ListView):
    model = Paciente
    template_name = 'core/paciente_list.html'
    context_object_name = 'pacientes'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('nome')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nome__icontains=query) | Q(cpf__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class PacienteCreateView(CreateView):
    model = Paciente
    fields = ['nome', 'telefone', 'email', 'data_nascimento', 'cpf', 'arquivo_exame_paciente', 'termo_paciente']
    template_name = 'core/paciente_form.html'
    success_url = reverse_lazy('paciente_list')

class PacienteUpdateView(UpdateView):
    model = Paciente
    fields = ['nome', 'telefone', 'email', 'data_nascimento', 'cpf', 'arquivo_exame_paciente', 'termo_paciente']
    template_name = 'core/paciente_form.html'
    success_url = reverse_lazy('paciente_list')

class ClinicaListView(ListView):
    model = Clinica
    template_name = 'core/clinica_list.html'
    context_object_name = 'clinicas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('nome')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(nome__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class ClinicaCreateView(CreateView):
    model = Clinica
    fields = ['nome', 'endereco', 'telefone']
    template_name = 'core/clinica_form.html'
    success_url = reverse_lazy('clinica_list')

class ClinicaUpdateView(UpdateView):
    model = Clinica
    fields = ['nome', 'endereco', 'telefone']
    template_name = 'core/clinica_form.html'
    success_url = reverse_lazy('clinica_list')

def relatorio_financeiro(request):
    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')
    clinica_id = request.GET.get('clinica')

    # Queryset base para todas as consultas pagas no período
    consultas_pagas_periodo = Consulta.objects.filter(pago=True)

    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            consultas_pagas_periodo = consultas_pagas_periodo.filter(data_consulta__gte=data_inicio)
        except ValueError:
            pass
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            consultas_pagas_periodo = consultas_pagas_periodo.filter(data_consulta__lte=data_fim)
        except ValueError:
            pass
    
    # Calcular o total geral arrecadado (antes de filtrar por clínica específica)
    total_geral_arrecadado = consultas_pagas_periodo.aggregate(total=Sum('valor'))['total'] or 0.00

    # Dicionário para armazenar relatórios por clínica
    relatorios_por_clinica = {}
    
    # Obter todas as clínicas para o filtro e para agrupar
    todas_clinicas = Clinica.objects.all().order_by('nome')

    # Se uma clínica específica foi selecionada, filtraremos apenas por ela
    if clinica_id:
        consultas_pagas_periodo = consultas_pagas_periodo.filter(clinica_id=clinica_id)
        
        # Para garantir que o relatório por clínica seja apenas para a selecionada
        clinica_selecionada_obj = todas_clinicas.filter(pk=clinica_id).first()
        if clinica_selecionada_obj:
            consultas_da_clinica = consultas_pagas_periodo.filter(clinica=clinica_selecionada_obj).order_by('-data_consulta', '-hora_inicio')
            total_arrecadado_clinica = consultas_da_clinica.aggregate(total=Sum('valor'))['total'] or 0.00
            if consultas_da_clinica.exists():
                relatorios_por_clinica[clinica_selecionada_obj.nome] = {
                    'clinica_obj': clinica_selecionada_obj,
                    'consultas': consultas_da_clinica,
                    'total_arrecadado': total_arrecadado_clinica,
                }
    else: # Se nenhuma clínica específica foi selecionada, mostra todas
        for clinica in todas_clinicas:
            consultas_da_clinica = consultas_pagas_periodo.filter(clinica=clinica).order_by('-data_consulta', '-hora_inicio')
            total_arrecadado_clinica = consultas_da_clinica.aggregate(total=Sum('valor'))['total'] or 0.00
            
            if consultas_da_clinica.exists():
                relatorios_por_clinica[clinica.nome] = {
                    'clinica_obj': clinica,
                    'consultas': consultas_da_clinica,
                    'total_arrecadado': total_arrecadado_clinica,
                }

    context = {
        'relatorios_por_clinica': relatorios_por_clinica,
        'todas_clinicas': todas_clinicas,
        'data_inicio': data_inicio_str,
        'data_fim': data_fim_str,
        'clinica_selecionada_id': int(clinica_id) if clinica_id else '',
        'total_geral_arrecadado': total_geral_arrecadado, # Novo: Total geral
    }
    return render(request, 'core/relatorio_financeiro.html', context)

def get_consultas_json(request):
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')

    print(f"\n--- Requisição FullCalendar ---")
    print(f"Parâmetros recebidos: start={start_str}, end={end_str}")

    consultas_qs = Consulta.objects.all()

    if start_str and end_str:
        try:
            start_date_obj = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end_date_obj = datetime.fromisoformat(end_str.replace('Z', '+00:00'))

            if settings.USE_TZ:
                start_date = timezone.make_aware(start_date_obj) if timezone.is_naive(start_date_obj) else start_date_obj
                end_date = timezone.make_aware(end_date_obj) if timezone.is_naive(end_date_obj) else end_date_obj
            else:
                start_date = start_date_obj
                end_date = end_date_obj
            
            # Abordagem de filtro no Python (para depuração e clareza):
            consultas_filtradas_em_memoria = []
            for consulta in consultas_qs:
                consulta_start_dt = timezone.make_aware(datetime.combine(consulta.data_consulta, consulta.hora_inicio))
                consulta_end_dt = timezone.make_aware(datetime.combine(consulta.data_consulta, consulta.hora_fim))

                # Verifica se o evento da consulta intercepta o período [start_date, end_date)
                if consulta_start_dt < end_date and consulta_end_dt > start_date:
                    consultas_filtradas_em_memoria.append(consulta)
            
            consultas_qs = consultas_filtradas_em_memoria # Usa a lista filtrada

            print(f"Datas de filtro (aware): start={start_date}, end={end_date}")
            # print(f"Query SQL gerada: {str(consultas_qs.query)}") # Não funciona mais com lista filtrada em memória

        except ValueError as e:
            print(f"ERRO ao converter datas do FullCalendar: {e}")
            pass

    events = []
    for consulta in consultas_qs: # Itera sobre a lista filtrada
        event_id = str(consulta.pk)
        
        # Obtém o nome do paciente e da clínica de forma segura
        paciente_nome_display = consulta.paciente.nome if consulta.paciente else 'Horário Reservado'
        clinica_nome_display = consulta.clinica.nome if consulta.clinica else 'N/A'

        event_title = f"{paciente_nome_display}"
        if consulta.procedimento:
            event_title += f" - {consulta.procedimento}"

        start_datetime = datetime.combine(consulta.data_consulta, consulta.hora_inicio)
        end_datetime = datetime.combine(consulta.data_consulta, consulta.hora_fim)

        if settings.USE_TZ:
            start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())
            end_datetime = timezone.make_aware(end_datetime, timezone.get_current_timezone())

        event_background_color = '#198754' if consulta.status == 'CONFIRMADO' else \
                               '#add8e6' if consulta.status == 'ATENDIDO' else \
                               '#dc3545' if consulta.status in ['CANCELADO', 'NAO_COMPARECEU'] else \
                               '#808080' if consulta.status == 'RESERVADO' else \
                               '#E0509B' # Agendado ou outros
        event_text_color = '#000000' if consulta.status == 'ATENDIDO' else '#ffffff'


        events.append({
            'id': event_id,
            'title': event_title,
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'url': reverse_lazy('editar_consulta', kwargs={'pk': consulta.pk}),
            'extendedProps': {
                'paciente_nome': paciente_nome_display, # Usar a variável segura
                'clinica_nome': clinica_nome_display,   # Usar a variável segura
                'status': consulta.get_status_display(),
                'procedimento': consulta.procedimento or 'Não especificado',
                'valor': f"R$ {consulta.valor:.2f}" if consulta.valor is not None else 'N/A',
                'pago': 'Sim' if consulta.pago else 'Não',
            },
            'backgroundColor': event_background_color,
            'borderColor': event_background_color,
            'textColor': event_text_color,
            'allDay': False,
        })
    
    print(f"Total de eventos retornados: {len(events)}")
    return JsonResponse(events, safe=False)
