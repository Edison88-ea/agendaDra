
from django.db import models
from django.contrib.auth.models import User

class Paciente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    exames = models.TextField(blank=True, null=True)
     

    def __str__(self):
        return self.nome

class Clinica(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nome

class Dentista(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    cro = models.CharField(max_length=20, unique=True)
    nome_completo = models.CharField(max_length=100)

    def __str__(self):
        return self.nome_completo

class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    dentista = models.ForeignKey(Dentista, on_delete=models.CASCADE, blank=True, null=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    data_hora = models.DateTimeField()
    procedimento = models.CharField(max_length=200, blank=True, null=True)
    valor = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    pago = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True, null=True)
    arquivo_exame = models.FileField(upload_to='exames/', blank=True, null=True)
    STATUS_CHOICES = [
        ('AGENDADO', 'Agendado'),
        ('CONFIRMADO', 'Confirmado'),
        ('ATENDIDO', 'Atendido'),
        ('CANCELADO', 'Cancelado'),
        ('NAO_COMPARECEU', 'Não Compareceu'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADO') # Novo campo


    class Meta:
        ordering = ['data_hora']
        unique_together = ('clinica', 'data_hora')

    def __str__(self):
        return f"Consulta de {self.paciente.nome} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"