from django import forms
from .models import Consulta

class ConsultaForm(forms.ModelForm):
    """
    Form for creating and updating Consulta objects.
    Uses datetime-local widget for data_hora.
    """
    class Meta:
        model = Consulta
        fields = ['paciente', 'clinica', 'data_hora', 'procedimento', 'valor', 'pago', 'observacoes', 'status', 'arquivo_exame'] # Adicionado 'arquivo_exame'
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }