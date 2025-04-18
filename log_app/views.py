from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import WorkLogForm
from .models import WorkLog
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncDate
from datetime import date, time, timedelta
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate
from django.utils.timezone import get_current_timezone



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

    return render(request, 'log_app/add_worklog.html', {
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


from django.db.models.functions import TruncDate
from django.db.models import Sum
from django.db.models import F, Func, ExpressionWrapper, DateTimeField
from django.utils.timezone import localtime
from django.utils import timezone
from datetime import timedelta

@login_required
def dashboard(request):
    # 1. Filter logs by user
    if request.user.is_superuser:
        user_logs = WorkLog.objects.all()
    else:
        user_logs = WorkLog.objects.filter(user=request.user)
    
    user_logs = user_logs.order_by('-date_logged')
    total_logs = user_logs.count()
    total_hours = sum(log.hours_spent for log in user_logs)
    recent_logs = user_logs[:5]

    # 2. Handle date range selection
    date_range = request.GET.get('range', 'week')
    today = timezone.localtime(timezone.now()).date()

    # Calculate date ranges
    if date_range == 'today':
        start_date = today
        end_date = today + timedelta(days=1)
        date_list = [today]
    elif date_range == 'month':
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=1)
        date_list = [start_date + timedelta(days=x) for x in range(31)]
    elif date_range == 'year':
        start_date = today - timedelta(days=365)
        end_date = today + timedelta(days=1)
        date_list = [today - timedelta(days=x) for x in range(0, 366, 30)]
    else:  # week
        start_date = today - timedelta(days=6)
        end_date = today + timedelta(days=1)
        date_list = [start_date + timedelta(days=x) for x in range(7)]

    # 3. Create timezone-aware datetime range (FIXED)
    from datetime import datetime, time
    start_datetime = timezone.make_aware(datetime.combine(start_date, time.min))
    end_datetime = timezone.make_aware(datetime.combine(end_date, time.min))

    # 4. Manual aggregation with timezone conversion
    hours_by_day = {}
    for log in user_logs.filter(date_logged__gte=start_datetime, date_logged__lt=end_datetime):
        log_date = timezone.localtime(log.date_logged).date()
        hours_by_day[log_date] = hours_by_day.get(log_date, 0) + log.hours_spent

    # 5. Prepare chart data
    labels = []
    data = []
    for day in date_list:
        labels.append(day.strftime('%a %b %d' if date_range == 'week' else '%b %d'))
        data.append(float(hours_by_day.get(day, 0)))

    return render(request, 'log_app/dashboard.html', {
        'total_logs': total_logs,
        'total_hours': total_hours,
        'recent_logs': recent_logs,
        'chart_labels': labels,
        'chart_data': data,
        'selected_range': date_range,
    })