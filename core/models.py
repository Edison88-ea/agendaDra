from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime

class Paciente(models.Model):
    """
    Representa um paciente.
    """
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    arquivo_exame_paciente = models.FileField(upload_to='pacientes_exames/', blank=True, null=True) 
    termo_paciente = models.FileField(upload_to='termos_pacientes/', blank=True, null=True) 

    def __str__(self):
        return self.nome

class Clinica(models.Model):
    """
    Representa uma clínica onde a dentista atende.
    """
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nome

class Dentista(models.Model):
    """
    Representa uma dentista. Pode ser associada a um usuário do Django.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    cro = models.CharField(max_length=20, unique=True)
    nome_completo = models.CharField(max_length=100)

    def __str__(self):
        return self.nome_completo

class Consulta(models.Model):
    """
    Representa uma consulta.
    """
    STATUS_CHOICES = [
        ('AGENDADO', 'Agendado'),
        ('CONFIRMADO', 'Confirmado'),
        ('ATENDIDO', 'Atendido'),
        ('CANCELADO', 'Cancelado'),
        ('NAO_COMPARECEU', 'Não Compareceu'),
        ('RESERVADO', 'Reservado'), # Novo status
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, blank=True, null=True) # Tornar opcional
    dentista = models.ForeignKey(Dentista, on_delete=models.SET_NULL, blank=True, null=True) # Tornar opcional
    clinica = models.ForeignKey(Clinica, on_delete=models.SET_NULL, blank=True, null=True) # Tornar opcional
    data_consulta = models.DateField("Data da Consulta")
    hora_inicio = models.TimeField("Horário de Início")
    hora_fim = models.TimeField("Horário de Fim")
    procedimento = models.CharField(max_length=200, blank=True, null=True)
    valor = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    pago = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADO')
    arquivo_exame = models.FileField(upload_to='exames/', blank=True, null=True) 

    class Meta:
        ordering = ['data_consulta', 'hora_inicio']
        # unique_together = ('clinica', 'data_consulta', 'hora_inicio') # Comentado para validação customizada

    def __str__(self):
        return f"Consulta de {self.paciente.nome if self.paciente else 'Horário Reservado'} em {self.data_consulta.strftime('%d/%m/%Y')} às {self.hora_inicio.strftime('%H:%M')}"

    def clean(self):
        # Validação para garantir que a hora de fim não seja anterior à hora de início
        if self.hora_inicio and self.hora_fim and self.hora_fim <= self.hora_inicio:
            raise ValidationError({'hora_fim': 'O horário de término deve ser posterior ao horário de início.'})
        super().clean()
