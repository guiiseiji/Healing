from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Especialidades, DadosMedico, is_medico
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
# Create your views here.


def cadastro_medico (request):
    
    
    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Você já está cadastrado!')
        return redirect ('/medicos/abrir_horario')
    
    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidades': especialidades})
    
    elif request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        valor_consulta = request.POST.get('valor_consulta')
        descricao = request.POST.get('descricao')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        
            
        dados_medico = DadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            valor_consulta=valor_consulta,
            descricao=descricao,
            cedula_identidade_medica=cim,
            rg=rg,
            foto=foto,
            especialidade_id=especialidade,
            user=request.user,
        )
        dados_medico.save()
        
        messages.add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso.')

        return redirect('/medicos/abrir_horario')
    