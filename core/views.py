from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import Paciente, Clinica, Consulta, TermoPacienteArquivo, ExamePacienteArquivo, ExameConsultaArquivo, TermoConsultaArquivo
from .forms import ConsultaForm, PacienteForm
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Sum, Q
from django.forms import inlineformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# FormSets para Paciente
TermoPacienteArquivoFormSet = inlineformset_factory(
    Paciente,
    TermoPacienteArquivo,
    fields=['arquivo', 'descricao'],
    extra=1,
    can_delete=True
)

ExamePacienteArquivoFormSet = inlineformset_factory(
    Paciente,
    ExamePacienteArquivo,
    fields=['arquivo', 'descricao'],
    extra=1,
    can_delete=True
)

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

class AgendarConsultaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = 'core/agendar_consulta_form.html'
    success_url = reverse_lazy('agenda')
    permission_required = ('core.add_consulta', 'core.can_add_consulta_files')

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
                initial_data['hora_fim'] = (datetime.strptime(hora_inicio_param, '%H:%M') + timedelta(minutes=30)).time()
            except ValueError:
                pass
        
        if initial_data:
            kwargs['initial'] = initial_data
            
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submitted_exames_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('exames_upload')] if self.request.POST else []
        context['submitted_termos_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('termos_upload')] if self.request.POST else []
        return context

    def form_valid(self, form):
        self.object = form.save() 
        
        exames_files = self.request.FILES.getlist('exames_upload')
        for f in exames_files:
            ExameConsultaArquivo.objects.create(consulta=self.object, arquivo=f)
            
        termos_files = self.request.FILES.getlist('termos_upload')
        for f in termos_files:
            TermoConsultaArquivo.objects.create(consulta=self.object, arquivo=f)
            
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form) # Já chama get_context_data que passa os submitted_files
        return self.render_to_response(context)


class ConsultaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = 'core/agendar_consulta_form.html'
    success_url = reverse_lazy('agenda')
    permission_required = 'core.change_consulta'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submitted_exames_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('exames_upload')] if self.request.POST else []
        context['submitted_termos_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('termos_upload')] if self.request.POST else []
        return context

    def form_valid(self, form):
        self.object = form.save()

        exames_files = self.request.FILES.getlist('exames_upload')
        for f in exames_files:
            ExameConsultaArquivo.objects.create(consulta=self.object, arquivo=f)

        termos_files = self.request.FILES.getlist('termos_upload')
        for f in termos_files:
            TermoConsultaArquivo.objects.create(consulta=self.object, arquivo=f)

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form) # Já chama get_context_data que passa os submitted_files
        return self.render_to_response(context)

class ConsultaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Consulta
    template_name = 'core/consulta_confirm_delete.html'
    success_url = reverse_lazy('agenda')
    permission_required = 'core.delete_consulta'

class PacienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Paciente
    template_name = 'core/paciente_confirm_delete.html'
    success_url = reverse_lazy('paciente_list')
    permission_required = 'core.delete_paciente'


class ExcluirExameConsultaArquivoView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ExameConsultaArquivo
    template_name = 'core/confirm_delete_arquivo.html'
    permission_required = 'core.delete_exameconsulta_arquivo'
    
    def get_success_url(self):
        return reverse_lazy('editar_consulta', kwargs={'pk': self.object.consulta.pk})

class ExcluirTermoConsultaArquivoView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TermoConsultaArquivo
    template_name = 'core/confirm_delete_arquivo.html'
    permission_required = 'core.delete_termoconsulta_arquivo'
    
    def get_success_url(self):
        return reverse_lazy('editar_consulta', kwargs={'pk': self.object.consulta.pk})

class ExcluirExamePacienteArquivoView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ExamePacienteArquivo
    template_name = 'core/paciente_delete_arquivo.html'
    permission_required = 'core.delete_examepaciente_arquivo'
    
    def get_success_url(self):
        return reverse_lazy('editar_paciente', kwargs={'pk': self.object.paciente.pk})

class ExcluirTermoPacienteArquivoView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TermoPacienteArquivo
    template_name = 'core/paciente_delete_arquivo.html'
    permission_required = 'core.delete_termopaciente_arquivo'
    
    def get_success_url(self):
        return reverse_lazy('editar_paciente', kwargs={'pk': self.object.paciente.pk})

class PacienteListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Paciente
    template_name = 'core/paciente_list.html'
    context_object_name = 'pacientes'
    paginate_by = 10
    permission_required = 'core.change_paciente'

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
        context['submitted_exames_paciente_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('exames_upload_paciente')] if self.request.POST else []
        context['submitted_termos_paciente_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('termos_upload_paciente')] if self.request.POST else []
        return context

class PacienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'core/paciente_form.html'
    success_url = reverse_lazy('paciente_list')
    permission_required = ('core.add_paciente', 'core.can_add_paciente_files')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['submitted_exames_paciente_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('exames_upload_paciente')]
            context['submitted_termos_paciente_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('termos_upload_paciente')]
        else:
            context['submitted_exames_paciente_files'] = []
            context['submitted_termos_paciente_files'] = []
        return context

    def form_valid(self, form):
        self.object = form.save()
        
        exames_files = self.request.FILES.getlist('exames_upload_paciente')
        for f in exames_files:
            ExamePacienteArquivo.objects.create(paciente=self.object, arquivo=f)
            
        termos_files = self.request.FILES.getlist('termos_upload_paciente')
        for f in termos_files:
            TermoPacienteArquivo.objects.create(paciente=self.object, arquivo=f)
            
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['submitted_exames_paciente_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('exames_upload_paciente')]
        context['submitted_termos_paciente_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('termos_upload_paciente')]
        return self.render_to_response(context)

class PacienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Paciente
    form_class = PacienteForm # Usar o novo PacienteForm
    template_name = 'core/paciente_form.html'
    success_url = reverse_lazy('paciente_list')
    permission_required = 'core.change_paciente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['submitted_exames_paciente_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('exames_upload_paciente')]
            context['submitted_termos_paciente_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('termos_upload_paciente')]
        else:
            context['submitted_exames_paciente_files'] = []
            context['submitted_termos_paciente_files'] = []
        return context

    def form_valid(self, form):
        self.object = form.save()
        
        exames_files = self.request.FILES.getlist('exames_upload_paciente')
        for f in exames_files:
            ExamePacienteArquivo.objects.create(paciente=self.object, arquivo=f)
            
        termos_files = self.request.FILES.getlist('termos_upload_paciente')
        for f in termos_files:
            TermoPacienteArquivo.objects.create(paciente=self.object, arquivo=f)
            
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['submitted_exames_paciente_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('exames_upload_paciente')]
        context['submitted_termos_paciente_files'] = [{'name': f.name, 'size': f.size} for f in self.request.FILES.getlist('termos_upload_paciente')]
        return self.render_to_response(context)

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

class ClinicaCreateView(LoginRequiredMixin, CreateView):
    model = Clinica
    fields = ['nome', 'endereco', 'telefone']
    template_name = 'core/clinica_form.html'
    success_url = reverse_lazy('clinica_list')

class ClinicaUpdateView(LoginRequiredMixin, UpdateView):
    model = Clinica
    fields = ['nome', 'endereco', 'telefone']
    template_name = 'core/clinica_form.html'
    success_url = reverse_lazy('clinica_list')
class ClinicaDeleteView(LoginRequiredMixin, DeleteView):
    model = Clinica
    template_name = 'core/clinica_confirm_delete.html'
    success_url = reverse_lazy('clinica_list')    

class RelatorioFinanceiroView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView): 
    template_name = 'core/relatorio_financeiro.html'
    login_url = '/accounts/login/' 
    permission_required = 'core.view_relatorio_financeiro'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request 

        data_inicio_str = request.GET.get('data_inicio')
        data_fim_str = request.GET.get('data_fim')
        clinica_id = request.GET.get('clinica')

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
        
        total_geral_arrecadado = consultas_pagas_periodo.aggregate(total=Sum('valor'))['total'] or 0.00

        relatorios_por_clinica = {}
        
        todas_clinicas = Clinica.objects.all().order_by('nome')

        if clinica_id:
            consultas_pagas_periodo = consultas_pagas_periodo.filter(clinica_id=clinica_id)
            
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
            else:
                for clinica in todas_clinicas:
                    consultas_da_clinica = consultas_pagas_periodo.filter(clinica=clinica).order_by('-data_consulta', '-hora_inicio')
                    total_arrecadado_clinica = consultas_da_clinica.aggregate(total=Sum('valor'))['total'] or 0.00
                    
                    if consultas_da_clinica.exists():
                        relatorios_por_clinica[clinica.nome] = {
                            'clinica_obj': clinica,
                            'consultas': consultas_da_clinica,
                            'total_arrecadado': total_arrecadado_clinica,
                        }

        context.update({ 
            'relatorios_por_clinica': relatorios_por_clinica,
            'todas_clinicas': todas_clinicas,
            'data_inicio': data_inicio_str,
            'data_fim': data_fim_str,
            'clinica_selecionada_id': int(clinica_id) if clinica_id else '',
            'total_geral_arrecadado': total_geral_arrecadado,
        })
        return context

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
            
            consultas_filtradas_em_memoria = []
            for consulta in consultas_qs:
                consulta_start_dt = timezone.make_aware(datetime.combine(consulta.data_consulta, consulta.hora_inicio))
                consulta_end_dt = timezone.make_aware(datetime.combine(consulta.data_consulta, consulta.hora_fim))

                if consulta_start_dt < end_date and consulta_end_dt > start_date:
                    consultas_filtradas_em_memoria.append(consulta)
            
            consultas_qs = consultas_filtradas_em_memoria

            print(f"Datas de filtro (aware): start={start_date}, end={end_date}")

        except ValueError as e:
            print(f"ERRO ao converter datas do FullCalendar: {e}")
            pass

    events = []
    for consulta in consultas_qs:
        event_id = str(consulta.pk)
        
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
                'paciente_nome': paciente_nome_display,
                'clinica_nome': clinica_nome_display,
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
# NOVO: View para retornar pacientes filtrados por clínica (para AJAX)
def get_pacientes_por_clinica(request):
    clinica_id = request.GET.get('clinica_id')
    pacientes = []
    if clinica_id:
        # Filtra pacientes que têm a clínica_principal associada
        pacientes_qs = Paciente.objects.filter(clinica_principal__id=clinica_id).order_by('nome')
        for paciente in pacientes_qs:
            pacientes.append({'id': paciente.id, 'nome': paciente.nome})
    return JsonResponse(pacientes, safe=False)