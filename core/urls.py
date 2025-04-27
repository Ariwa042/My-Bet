from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='index'),
    path('leagues/<int:league_id>/', views.league_detail, name='league_detail'),
   # path('teams/', views.team_list, name='team_list'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('matches/', views.match_list, name='match_list'),
    path('matches/<int:match_id>/', views.match_detail, name='match_detail'),
    path('deposit/', views.deposit, name='deposit'),
    path('deposit_info/', views.deposit_instructions, name='deposit_instructions'),
    path('withdraw/', views.withdrawal, name='withdrawal'),
    path('transactions/', views.transaction_history, name='transaction_history'),

    ]