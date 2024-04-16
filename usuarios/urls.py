from django.urls import path
from . import views


urlpatterns = [
    path('cadastro/', views.cadastro, name="cadastro"), #função cadastro dentro de views
    path ('login/', views.login_view, name='login'),
    path ('logout/', views.logout, name='logout')
    
]