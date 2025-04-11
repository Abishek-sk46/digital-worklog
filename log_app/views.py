from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import WorkLogForm
from .models import WorkLog
from django.contrib.auth.decorators import login_required



def home(request):
    return render(request,'log_app/home.html')


@login_required
def worklog_list(request):
    if request.user.is_superuser:
        worklogs = WorkLog.objects.all()
    else:
        worklogs = WorkLog.objects.filter(user=request.user)
    return render(request, 'log_app/worklog_list.html', {'worklogs': worklogs})


@login_required
def add_worklog(request):
    if request.method == 'POST':
        form = WorkLogForm(request.POST)
        if form.is_valid():
            worklog = form.save(commit=False)
            worklog.user = request.user  # 🔥 Auto-assign user
            worklog.save()
            return redirect('worklog_list')
    else:
        form = WorkLogForm()
    
    return render(request, 'log_app/add_worklog.html', {
        'form': form,
        'title': 'Add Work Log'
    })

from django.shortcuts import get_object_or_404

@login_required
def edit_worklog(request, pk):
    worklog = get_object_or_404(WorkLog, pk=pk)

    # 🛑 Block other users
    if worklog.user != request.user:
        return redirect('worklog_list')

    if request.method == 'POST':
        form = WorkLogForm(request.POST, instance=worklog)
        if form.is_valid():
            form.save()
            return redirect('worklog_list')
    else:
        form = WorkLogForm(instance=worklog)

    return render(request, 'log_app/edit_worklog.html', {
        'form': form,
        'title': 'Edit Work Log'
    })

@login_required
def delete_worklog(request, pk):
    worklog = get_object_or_404(WorkLog, pk=pk)

    # 🛑 Only the owner can delete
    if worklog.user == request.user:
        worklog.delete()

    return redirect('worklog_list')


from django.contrib.auth import login
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Optional: auto login after register
            return redirect('worklog_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})
