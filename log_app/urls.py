from django.urls import path
from . import views


urlpatterns = [
    path('',views.home,name='home'),
    path('list/', views.worklog_list, name='worklog_list'),  
    path('add/', views.add_worklog, name='add_worklog'),
    path('edit/<int:pk>/', views.edit_worklog, name='edit_worklog'),
    path('delete/<int:pk>/', views.delete_worklog, name='delete_worklog'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # for forget password
    path('password-reset/', views.custom_password_reset, name='custom_password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    path('export/', views.export_csv, name='export_csv'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),

    # =============================Team========================================
    path('teams/create/', views.create_team, name='create_team'),
    path('teams/<int:team_id>/', views.team_dashboard, name='team_dashboard'),
    path('api/users/', views.user_search_api, name='user_search_api'),
]