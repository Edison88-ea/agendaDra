from django import forms
from .models import Consulta, Paciente 

# Campo de formulário customizado para múltiplos arquivos (já existente)
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ConsultaForm(forms.ModelForm):
    exames_upload = MultipleFileField(label="Carregar Exames (multiplos)", required=False)
    termos_upload = MultipleFileField(label="Carregar Termos (multiplos)", required=False)

    class Meta:
        model = Consulta
        fields = ['paciente', 'clinica', 'data_consulta', 'hora_inicio', 'hora_fim', 'procedimento', 'valor', 'pago', 'status', 'observacoes']
        widgets = {
            'data_consulta': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_consulta = cleaned_data.get("data_consulta")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fim = cleaned_data.get("hora_fim")
        status = cleaned_data.get("status")
        paciente = cleaned_data.get("paciente")
        clinica = cleaned_data.get("clinica")

        if hora_inicio and hora_fim and hora_fim <= hora_inicio:
            self.add_error('hora_fim', "O horário de término deve ser posterior ao horário de início.")

        if status != 'RESERVADO':
            if not paciente:
                self.add_error('paciente', "Paciente é obrigatório para este status.")
            if not clinica:
                self.add_error('clinica', "Clínica é obrigatória para este status.")
        else:
            if paciente:
                self.add_error('paciente', "Não é possível associar um paciente a um horário reservado. Mude o status ou remova o paciente.")
            if clinica:
                self.add_error('clinica', "Não é possível associar uma clínica a um horário reservado. Mude o status ou remova a clínica.")

        if data_consulta and hora_inicio and hora_fim:
            conflitos = Consulta.objects.filter(
                data_consulta=data_consulta
            ).exclude(pk=self.instance.pk if self.instance else None)

            for c in conflitos:
                if c.hora_inicio and c.hora_fim:
                    if hora_inicio < c.hora_fim and hora_fim > c.hora_inicio:
                        if c.status != 'RESERVADO' and status != 'RESERVADO':
                            self.add_error(None, f"Já existe uma consulta agendada para este horário ou que se sobrepõe a este período na clínica {c.clinica}.")
                        elif status != 'RESERVADO' and c.status == 'RESERVADO':
                             self.add_error(None, f"Este horário está reservado e não pode ser agendado para uma consulta.")
                        elif status == 'RESERVADO' and c.status != 'RESERVADO':
                             self.add_error(None, f"Não é possível reservar este horário, pois já existe uma consulta agendada.")
                        elif status == 'RESERVADO' and c.status == 'RESERVADO':
                            pass
                        else:
                            self.add_error(None, "Conflito de horário não permitido.")
        
        return cleaned_data

# Formulário para o modelo Paciente
class PacienteForm(forms.ModelForm):
    exames_upload_paciente = MultipleFileField(label="Carregar Exames do Paciente (multiplos)", required=False)
    termos_upload_paciente = MultipleFileField(label="Carregar Termos do Paciente (multiplos)", required=False)

    class Meta:
        model = Paciente
        fields = ['nome', 'telefone', 'email', 'data_nascimento', 'cpf', 'clinica_principal', 'observacoes']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}), 
        }
