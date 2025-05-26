from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import Paciente, Clinica, Consulta, Dentista
from .forms import ConsultaForm
from django.http import JsonResponse
from django.conf import settings # Adicione esta importação
import os # Adicione esta importação
from django.db.models import Sum # Importe Sum para agregação
from django.db.models import Q

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
        
        return Consulta.objects.filter(data_hora__date__gte=start_of_week, data_hora__date__lte=end_of_week).order_by('data_hora')

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
            data_consulta = consulta.data_hora.date()
            if data_consulta not in consultas_por_data:
                consultas_por_data[data_consulta] = []
            consultas_por_data[data_consulta].append(consulta)
        context['consultas_por_data'] = consultas_por_data

        prev_week_start = start_of_week - timedelta(weeks=1)
        next_week_start = start_of_week + timedelta(weeks=1)
        context['prev_week_url'] = f"{reverse_lazy('agenda')}?year={prev_week_start.year}&month={prev_week_start.month}&day={prev_week_start.day}"
        context['next_week_url'] = f"{reverse_lazy('agenda')}?year={next_week_start.year}&month={next_week_start.month}&day={next_week_start.day}"
        
        return context

# Certifique-se que esta classe está definida corretamente
class AgendarConsultaCreateView(CreateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = 'core/agendar_consulta_form.html'
    success_url = reverse_lazy('agenda')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Se você tem o modelo Dentista e quer pré-selecionar:
        # if Dentista.objects.exists():
        #     kwargs['initial']['dentista'] = Dentista.objects.first()
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
    paginate_by = 10  # Adiciona paginação, se desejar

    def get_queryset(self):
        queryset = super().get_queryset().order_by('nome') # Ordena por nome por padrão
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nome__icontains=query) | Q(cpf__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '') # Passa o termo de busca para o template
        return context

class PacienteCreateView(CreateView):
    model = Paciente
    fields = ['nome', 'telefone', 'email', 'data_nascimento', 'cpf', 'exames']
    template_name = 'core/paciente_form.html'
    success_url = reverse_lazy('paciente_list')

class PacienteUpdateView(UpdateView):
    model = Paciente
    fields = ['nome', 'telefone', 'email', 'data_nascimento', 'cpf', 'exames']
    template_name = 'core/paciente_form.html'
    success_url = reverse_lazy('paciente_list')

class ClinicaListView(ListView):
    model = Clinica
    template_name = 'core/clinica_list.html'
    context_object_name = 'clinicas'
    paginate_by = 10 # Adiciona paginação

    def get_queryset(self):
        queryset = super().get_queryset().order_by('nome') # Ordena por nome
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(nome__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '') # Passa o termo de busca para o template
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

    consultas = Consulta.objects.filter(pago=True)
    total_arrecadado = 0

    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            consultas = consultas.filter(data_hora__date__gte=data_inicio)
        except ValueError:
            pass
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            consultas = consultas.filter(data_hora__date__lte=data_fim)
        except ValueError:
            pass
    
    total_arrecadado = consultas.aggregate(total=Sum('valor'))['total'] or 0.00

    context = {
        'consultas': consultas.order_by('-data_hora'),
        'total_arrecadado': total_arrecadado,
        'data_inicio': data_inicio_str,
        'data_fim': data_fim_str,
    }
    return render(request, 'core/relatorio_financeiro.html', context)

def get_consultas_json(request):
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')

    consultas_qs = Consulta.objects.all()

    if start_str and end_str:
        try:
            start_date_naive = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end_date_naive = datetime.fromisoformat(end_str.replace('Z', '+00:00'))

            start_date = timezone.make_aware(start_date_naive) if timezone.is_naive(start_date_naive) else start_date_naive
            end_date = timezone.make_aware(end_date_naive) if timezone.is_naive(end_date_naive) else end_date_naive
            
            consultas_qs = consultas_qs.filter(data_hora__gte=start_date, data_hora__lt=end_date)
            
        except ValueError as e:
            print(f"ERRO ao parsear datas do FullCalendar: {e}")
            pass

    events = []
    for consulta in consultas_qs:
        event_id = str(consulta.pk)
        event_title = f"{consulta.paciente.nome}"
        if consulta.procedimento:
            event_title += f" - {consulta.procedimento}"

        # Define a cor do evento com base no status
        if consulta.status == 'ATENDIDO':
            event_background_color = '#add8e6'  # Azul claro para Atendido
            event_text_color = '#000000'       # Texto preto para melhor contraste
        elif consulta.status == 'CANCELADO' or consulta.status == 'NAO_COMPARECEU':
            event_background_color = '#dc3545'  # Vermelho para Cancelado/Não Compareceu
            event_text_color = '#ffffff'       # Texto branco
        elif consulta.status == 'CONFIRMADO':
            event_background_color = '#198754'  # Verde para Confirmado
            event_text_color = '#ffffff'       # Texto branco
        elif consulta.status == 'AGENDADO':
            event_background_color = '#E0509B'  # Rosa escuro
            event_text_color = '#ffffff'       # Texto branco

        events.append({
            'id': event_id,
            'title': event_title,
            'start': consulta.data_hora.isoformat(),
            'end': (consulta.data_hora + timedelta(minutes=30)).isoformat(), # Ajuste conforme a duração da consulta
            'url': reverse_lazy('editar_consulta', kwargs={'pk': consulta.pk}),
            'extendedProps': {
                'paciente_nome': consulta.paciente.nome,
                'clinica_nome': consulta.clinica.nome,
                'status': consulta.get_status_display(), # Usando o valor legível para o tooltip
                'procedimento': consulta.procedimento or 'Não especificado',
                'valor': f"R$ {consulta.valor:.2f}" if consulta.valor is not None else 'N/A',
                'pago': 'Sim' if consulta.pago else 'Não',
            },
            'backgroundColor': event_background_color,
            'borderColor': event_background_color, # Geralmente a mesma cor do fundo
            'textColor': event_text_color,
            'allDay': False,
        })

    print(f"Total de eventos retornados: {len(events)}")
    return JsonResponse(events, safe=False)