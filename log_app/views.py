from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import WorkLogForm
from .models import WorkLog


def home(request):
    return render(request,'log_app/home.html')

def worklog_list(request):
    worklogs = WorkLog.objects.all()  # Fetch all worklogs from the database
    return render(request, 'log_app/worklog_list.html', {'worklogs': worklogs})

def add_worklog(request):
    if request.method == 'POST':
        form = WorkLogForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('worklog_list')
    else:
        form = WorkLogForm()
    users = User.objects.all()
    return render(request, 'log_app/add_worklog.html', {'form': form, 'title': 'Add Work Log', 'users':users})

from django.shortcuts import get_object_or_404

def edit_worklog(request, pk):
    worklog = get_object_or_404(WorkLog, pk=pk)
    if request.method == 'POST':
        form = WorkLogForm(request.POST, instance=worklog)
        if form.is_valid():
            form.save()
            return redirect('worklog_list')  # Redirect to your worklog list view
    else:
        form = WorkLogForm(instance=worklog)
    users = User.objects.all()
    return render(request, 'log_app/add_worklog.html', {'form': form, 'title': 'Edit Work Log','users':users})


def delete_worklog(request, pk):
    worklog = get_object_or_404(WorkLog, pk=pk)
    if request.method == 'POST':
        worklog.delete()
        return redirect('working_list')
    return render(request, 'log_app/delete_worklog.html', {'worklog': worklog})