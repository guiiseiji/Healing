from django.shortcuts import render
from medico.models import DadosMedico, Especialidades


# Create your views here.

def home(request):
    if request.method == "GET":
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        
        if medico_filtrar:
            medicos = medicos.filter (nome__icontains = medico_filtrar)
            
        if especialidades_filtrar:
            medicos = medicos.filter (especialidades_id__in=especialidades_filtrar)
        
        medicos = DadosMedico.objects.all()
        especialidades = Especialidades.objects.all()
        return render(request, 'home.html', {'medicos': medicos, 'especialidades':especialidades})
    
    
