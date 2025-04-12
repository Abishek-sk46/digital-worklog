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


@login_required
def dashboard(request):
    # 🔥 FIRST FIX: Filter by current user (or all for superuser)
    if request.user.is_superuser:
        user_logs = WorkLog.objects.all()
    else:
        user_logs = WorkLog.objects.filter(user=request.user)
    
    user_logs = user_logs.order_by('-date_logged')
    total_logs = user_logs.count()
    total_hours = sum(log.hours_spent for log in user_logs)
    recent_logs = user_logs[:5]

    date_range = request.GET.get('range', 'week')

    # Calculate date ranges
    today = timezone.localtime(timezone.now()).date()
    if date_range == 'today':
        start_date = today
        date_list = [today]
    elif date_range == 'month':
        start_date = today - timedelta(days=30)
        date_list = [start_date + timedelta(days=x) for x in range(31)]
    elif date_range == 'year':
        start_date = today - timedelta(days=365)
        date_list = [today - timedelta(days=x) for x in range(0, 366, 30)]
    else:  # week
        start_date = today - timedelta(days=6)
        date_list = [start_date + timedelta(days=x) for x in range(7)]

    # 🔥 SECOND FIX: Proper timezone-aware filtering
    daily_data = (
    user_logs
    .filter(date_logged__date__gte=start_date)
    .annotate(
        day=TruncDate('date_logged', tzinfo=get_current_timezone())  # ← KEY FIX
    )
    .values('day')
    .annotate(total_hours=Sum('hours_spent'))
    .order_by('day')
)

    hours_by_day = {log['day'].date(): log['total_hours'] for log in daily_data}

    labels = []
    data = []
    for day in date_list:
        labels.append(day.strftime('%a %b %d' if date_range == 'week' else '%b %d'))
        data.append(float(hours_by_day.get(day, 0)))



    # for testing
    print("=== CHART DEBUG START ===")

    print(f"Selected Range: {date_range}")
    print(f"Start Date: {start_date}")

    print("All Logs (user_logs):")
    for log in user_logs:
        print(f"📝 {log.task_list} | {log.date_logged} | {log.hours_spent}")

    print("\nFiltered Logs for Chart (daily_data):")
    for log in daily_data:
        print(f"📊 {log['day']} | {log['total_hours']} hrs")

    print(f"\nLabels: {labels}")
    print(f"Data: {data}")
    print("=== CHART DEBUG END ===")

    # 🔥 THIRD FIX: Proper empty state check
    if date_range == 'today' and not hours_by_day.get(today, 0):
        return render(request, 'log_app/dashboard.html', {
            'empty_today': True,
            'total_logs': total_logs,
            'total_hours': total_hours,
            'recent_logs': recent_logs,
            'selected_range': date_range,
        })

    return render(request, 'log_app/dashboard.html', {
        'total_logs': total_logs,
        'total_hours': total_hours,
        'recent_logs': recent_logs,
        'chart_labels': labels,
        'chart_data': data,
        'selected_range': date_range,
    })