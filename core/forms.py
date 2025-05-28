from django import forms
from .models import Consulta

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['paciente', 'clinica', 'data_consulta', 'hora_inicio', 'hora_fim', 'procedimento', 'valor', 'pago', 'status', 'observacoes', 'arquivo_exame']
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

        # Validação para garantir que a hora de fim não seja anterior à hora de início
        if hora_inicio and hora_fim and hora_fim <= hora_inicio:
            self.add_error('hora_fim', "O horário de término deve ser posterior ao horário de início.")

        # Validação condicional para paciente e clínica
        if status != 'RESERVADO':
            if not paciente:
                self.add_error('paciente', "Paciente é obrigatório para este status.")
            if not clinica:
                self.add_error('clinica', "Clínica é obrigatória para este status.")
        else: # Se o status for 'RESERVADO', podemos limpar paciente e clínica
            if paciente:
                self.add_error('paciente', "Não é possível associar um paciente a um horário reservado. Mude o status ou remova o paciente.")
            if clinica:
                self.add_error('clinica', "Não é possível associar uma clínica a um horário reservado. Mude o status ou remova a clínica.")


        # Lógica para verificar sobreposição de agendamentos (se já implementada)
        if data_consulta and hora_inicio and hora_fim:
            # Excluir a própria instância se estiver editando
            conflitos = Consulta.objects.filter(
                data_consulta=data_consulta
            ).exclude(pk=self.instance.pk if self.instance else None)

            for c in conflitos:
                # Se a consulta existente está reservada e a nova também, ou se sobrepõem
                # ou se a nova consulta não está reservada e se sobrepõe a qualquer uma
                if c.hora_inicio and c.hora_fim:
                    # Verifica sobreposição de horários
                    if hora_inicio < c.hora_fim and hora_fim > c.hora_inicio:
                        # Se a consulta existente não está reservada E a nova não está reservada
                        if c.status != 'RESERVADO' and status != 'RESERVADO':
                            raise forms.ValidationError(f"Já existe uma consulta agendada para este horário ou que se sobrepõe a este período na clínica {c.clinica}.")
                        # Se a nova consulta não está reservada mas se sobrepõe a uma reservada
                        elif status != 'RESERVADO' and c.status == 'RESERVADO':
                             raise forms.ValidationError(f"Este horário está reservado e não pode ser agendado para uma consulta.")
                        # Se a nova consulta está reservada mas se sobrepõe a uma não reservada
                        elif status == 'RESERVADO' and c.status != 'RESERVADO':
                             raise forms.ValidationError(f"Não é possível reservar este horário, pois já existe uma consulta agendada.")
                        # Se ambas são reservadas e se sobrepõem (permitido ou não, dependendo da regra de negócio)
                        # Por padrão, vamos permitir sobreposição de RESERVADO com RESERVADO, mas não com AGENDADO/ATENDIDO
                        # Se você quiser que RESERVADO não se sobreponha a NADA, remova o 'else' abaixo.
                        elif status == 'RESERVADO' and c.status == 'RESERVADO':
                            pass # Permite que horários RESERVADOS se sobreponham a outros RESERVADOS
                        else:
                            # Caso genérico de sobreposição não tratado acima (deveria ser erro)
                            raise forms.ValidationError("Conflito de horário não permitido.")
        
        return cleaned_data
