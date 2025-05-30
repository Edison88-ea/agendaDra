from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Paciente(models.Model):
    """
    Representa um paciente.
    """
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    observacoes = models.TextField("Observações", blank=True, null=True)
    clinica_principal = models.ForeignKey('Clinica', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Clínica Principal")

    def __str__(self):
        return self.nome

class ExamePacienteArquivo(models.Model):
    """
    Representa um arquivo de exame associado a um paciente.
    Permite múltiplos arquivos de exame por paciente.
    """
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='exames_arquivos')
    arquivo = models.FileField(upload_to='pacientes_exames/')
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição do Exame")
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Exame do Paciente"
        verbose_name_plural = "Exames do Paciente"
        ordering = ['-data_upload']

    def __str__(self):
        return f"Exame de {self.paciente.nome} - {self.descricao or self.arquivo.name}"

class TermoPacienteArquivo(models.Model):
    """
    Representa um arquivo de termo associado a um paciente.
    Permite múltiplos arquivos por paciente.
    """
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='termos_arquivos')
    arquivo = models.FileField(upload_to='termos_pacientes/')
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição do Termo")
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Termo do Paciente"
        verbose_name_plural = "Termos do Paciente"
        ordering = ['-data_upload']

    def __str__(self):
        return f"Termo de {self.paciente.nome} - {self.descricao or self.arquivo.name}"

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
        ('RESERVADO', 'Reservado'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, blank=True, null=True)
    dentista = models.ForeignKey(Dentista, on_delete=models.SET_NULL, blank=True, null=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.SET_NULL, blank=True, null=True)
    data_consulta = models.DateField("Data da Consulta")
    hora_inicio = models.TimeField("Horário de Início")
    hora_fim = models.TimeField("Horário de Fim")
    procedimento = models.CharField(max_length=200, blank=True, null=True)
    valor = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    pago = models.BooleanField(default=False)
    observacoes = models.TextField("Observações", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADO')
    

    class Meta:
        ordering = ['data_consulta', 'hora_inicio']

    def __str__(self):
        return f"Consulta de {self.paciente.nome if self.paciente else 'Horário Reservado'} em {self.data_consulta.strftime('%d/%m/%Y')} às {self.hora_inicio.strftime('%H:%M')}"

    def clean(self):
        if self.hora_inicio and self.hora_fim and self.hora_fim <= self.hora_inicio:
            raise ValidationError({'hora_fim': 'O horário de término deve ser posterior ao horário de início.'})
        super().clean()

class ExameConsultaArquivo(models.Model):
    """
    Representa um arquivo de exame associado a uma consulta.
    Permite múltiplos arquivos de exame por consulta.
    """
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='exames_consulta_arquivos')
    arquivo = models.FileField(upload_to='consultas_exames/')
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição do Exame da Consulta")
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Exame da Consulta"
        verbose_name_plural = "Exames da Consulta"
        ordering = ['-data_upload']

    def __str__(self):
        return f"Exame da Consulta {self.consulta.id} - {self.descricao or self.arquivo.name}"

class TermoConsultaArquivo(models.Model):
    """
    Representa um arquivo de termo associado a uma consulta.
    Permite múltiplos arquivos de termo por consulta.
    """
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='termos_consulta_arquivos')
    arquivo = models.FileField(upload_to='consultas_termos/')
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição do Termo da Consulta")
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Termo da Consulta"
        verbose_name_plural = "Termos da Consulta"
        ordering = ['-data_upload']

    def __str__(self):
        return f"Termo da Consulta {self.consulta.id} - {self.descricao or self.arquivo.name}"
