from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from .forms import WorkLogForm
from .models import WorkLog
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages 
from django.core.paginator import Paginator
from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.shortcuts import get_object_or_404
from .forms import ProfileForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.utils.http import urlsafe_base64_decode

import csv
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import io









def home(request):
    return render(request,'log_app/home.html')


@login_required

def worklog_list(request):
    if request.user.is_superuser:
        logs = WorkLog.objects.all().order_by('-date_logged')
    else:
        logs = WorkLog.objects.filter(user=request.user).order_by('-date_logged')
    
    paginator = Paginator(logs, 10)  # Show 10 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'log_app/worklog_list.html', {'page_obj': page_obj,'logs':logs})

@login_required
def add_worklog(request):
    if request.method == 'POST':
        form = WorkLogForm(request.POST)
        if form.is_valid():
            worklog = form.save(commit=False)
            worklog.user = request.user  # 🔥 Auto-assign user
            worklog.save()
            messages.success(request, "Worklog added successfully!")  # Add this line
            return redirect('worklog_list')
    else:
        form = WorkLogForm()
    
    return render(request, 'log_app/add_worklog.html', {
        'form': form,
        'title': 'Add Work Log'
    })


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
            messages.success(request, "Worklog updated successfully!") 
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


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Or wherever you want to redirect
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'log_app/edit_profile.html', {'form': form})


def custom_password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # You can customize email sending here
            form.save(request=request)  # Uses Django's default email sending mechanism
            messages.success(request, "Password reset email sent!")
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    
    return render(request, 'registration/password_reset_form.html', {'form': form})

# views.py
from django.shortcuts import render

def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')

# views.py

def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user)
    else:
        return render(request, 'registration/password_reset_invalid.html')  # Invalid link

    return render(request, 'registration/password_reset_confirm.html', {'form': form})

# views.py
from django.shortcuts import render

def password_reset_complete(request):
    return render(request, 'registration/password_reset_complete.html')


def export_csv(request):
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="worklogs_{timezone.now().date()}.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write headers
    writer.writerow(['Task Name', 'Description', 'Hours Spent', 'Date Logged'])
    
    # Get logs for current user
    logs = WorkLog.objects.filter(user=request.user).order_by('-date_logged')
    
    # Write data rows
    for log in logs:
        writer.writerow([
            log.task_list,
            log.description,
            log.hours_spent,
            timezone.localtime(log.date_logged).strftime('%Y-%m-%d %H:%M')
        ])
    
    return response




# In views.py

def export_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='RightAlign', alignment=2))  # 2 = TA_RIGHT
    
    # Content
    elements = []
    
    # Header
    elements.append(Paragraph(f"Work Logs for <b>{request.user.username}</b>", styles['Title']))
    elements.append(Paragraph(f"Generated on {timezone.now().date()}", styles['RightAlign']))
    elements.append(Spacer(1, 0.25 * inch))
    
    # Table Data
    data = [['Task', 'Hours', 'Date']]
    logs = WorkLog.objects.filter(user=request.user).order_by('-date_logged')
    
    for log in logs:
        data.append([
            log.task_list,
            f"{log.hours_spent:.2f}",
            timezone.localtime(log.date_logged).strftime('%b %d, %Y')
        ])
    
    # Create Table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3b82f6')),  # Header blue
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')