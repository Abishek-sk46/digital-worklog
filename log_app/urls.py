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

]