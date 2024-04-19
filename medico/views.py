from django.shortcuts import render, redirect
from .models import Especialidades, DadosMedico, is_medico, DatasAbertas
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
from datetime import datetime, timedelta
from paciente.models import Consulta, Documento

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
    
    
def abrir_horario (request):
    
    if not is_medico (request.user):
        messages.add_message(request, constants.WARNING, "Apenas médicos podem agendar horários")
        return redirect ('/usuarios/sair')
    
    if request.method == "GET":
        dados_medicos = DadosMedico.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        return render(request, 'abrir_horario.html', {'dados_medicos': dados_medicos, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
    
    elif request.method == "POST":
        data = request.POST.get('data') 
        data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M')
        
        if data_formatada <= datetime.now():
            messages.add_message(request, messages.WARNING, 'Data indisponível')
            return redirect ('/medicos/abrir_horario')           
    
        horario_abrir = DatasAbertas(
            data = data,
            user = request.user
        )
        
        horario_abrir.save ()
        
        messages.add_message(request, constants.SUCCESS, "Horário marcado com sucesso")
        return redirect ('/medicos/abrir_horario')
    
def consultas_medico (request):
    if not is_medico (request.user):
        messages.add_message(request, constants.WARNING, "Página exclusiva para médicos")
        return redirect ('/usuarios/sair')
    
    hoje = datetime.now().date()
    consultas_hoje = Consulta.objects.filter(data_aberta__user = request.user).filter(data_aberta__data__gte = hoje).filter(data_aberta__data__lt = hoje + timedelta(days=1))
    consultas_proximas = Consulta.objects.exclude (id__in = consultas_hoje.values('id')).filter(data_aberta__user=request.user)
    
    return render (request, 'consultas_medico.html', {'consultas_hoje':consultas_hoje, 'consultas_proximas': consultas_proximas, 'is_medico': is_medico(request.user)})


def consulta_area_medico(request, id_consulta):
    if not is_medico (request.user):
        messages.add_message(request, constants.WARNING, "Página exclusiva para médicos")
        return redirect ('/usuarios/sair')
    
    if request.method == "GET":
        consulta = Consulta.objects.get (id = id_consulta)
        documentos = Documento.objects.filter(consulta = consulta)
        return render (request, 'consulta_area_medico.html', {'consulta':consulta, 'documentos': documentos})
    
    elif request.method == "GET":
        consulta = Consulta.objects.get (id = id_consulta)
        link = request.POST.get ('link')
        
        if consulta.status == 'C':
            messages.add_message (request, constants.WARNING, 'Essa consulta foi cancelada')
            return redirect (f'/medicos/consulta_medico/{id_consulta}' )
        
        elif consulta.status == 'F':
            messages.add_message (request, constants.WARNING, 'Essa consulta foi finalizada')
            return redirect (f'/medicos/consulta_medico/{id_consulta}' )
        
        consulta.link = link 
        consulta.status = 'I'
        consulta.save()
        messages.add_message (request, constants.SUCCESS, 'Consulta inicializada')
        return redirect (f'/medicos/consulta_medico/{id_consulta}')
    
def finalizar_consulta(request, id_consulta):
    if not is_medico (request.user):
        messages.add_message(request, constants.WARNING, "Página exclusiva para médicos")
        return redirect ('/usuarios/sair')
    
    consulta = Consulta.objects.get (id = id_consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, "Essa consulta não é sua!")
        return redirect (f'/medicos/abrir_horario/')
    
    consulta.status = 'F'
    consulta.save()
    return redirect (f'/medicos/consulta_area_medico/{id_consulta}')


def add_documento (request, id_consulta):
    if not is_medico (request.user):
        messages.add_message(request, constants.WARNING, "Página exclusiva para médicos")
        return redirect ('/usuarios/sair')
    
    consulta = Consulta.objects.get (id = id_consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, "Essa consulta não é sua!")
        return redirect (f'/medicos/consulta_area_medico/{id_consulta}')
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')
    
    if not documento:
        messages.add_message(request, constants.ERROR, "Anexe o documento")
        return redirect (f'/medicos/consulta_area_medico/{id_consulta}')

        
    documento = Documento(
        consulta = consulta,
        titulo = titulo,
        documento = documento
    )
    
    documento.save()
    messages.add_message(request, constants.SUCCESS, "Documento anexado com sucesso")
    return redirect (f'/medicos/consulta_area_medico/{id_consulta}')

        
    
    
    
    
    