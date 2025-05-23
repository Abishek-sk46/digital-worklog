# Django imports for authentication and user management
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator

# Django imports for HTTP handling and shortcuts
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse

# Django imports for forms and models
from .forms import WorkLogForm, UserRegistrationForm, ProfileForm
from .models import WorkLog

# Django imports for utilities
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.core.paginator import Paginator
from django.contrib import messages

# Python standard library imports
from datetime import timedelta
import csv
import io

# ReportLab imports for PDF generation
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

# search functinality
from django.db.models import Q, Sum






def home(request):
    return render(request,'log_app/home.html')


@login_required

def worklog_list(request):
    search_query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'all')  # all/personal/team

    # Base query
    if request.user.is_superuser:
        logs = WorkLog.objects.all()
    else:
        logs = WorkLog.objects.filter(
            Q(user=request.user) |
            Q(team__members=request.user, visibility='TEAM') |
            Q(visibility='PUBLIC')
        )

    # Apply filters
    if filter_type == 'personal':
        logs = logs.filter(team__isnull=True)  # Only personal logs
    elif filter_type == 'team':
        logs = logs.filter(
            team__isnull=False,  # Only team-associated logs
            visibility='TEAM',   # Ensure visibility is set to 'TEAM'
            team__members=request.user  # Ensure the user is a member of the team
        )

    # Search
    if search_query:
        logs = logs.filter(
            Q(task_list__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    paginator = Paginator(logs.order_by('-date_logged'), 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'log_app/worklog_list.html', {
        'page_obj': page_obj,
        'logs': page_obj.object_list,
        'search_query': search_query,
        'current_filter': filter_type
    })

def add_worklog(request):
    if request.method == 'POST':
        form = WorkLogForm(request.POST)
        if form.is_valid():
            worklog = form.save(commit=False)
            worklog.user = request.user
            
            # Handle team assignment
            team_id = request.POST.get('team')
            if team_id:
                worklog.team = Team.objects.get(id=team_id)
            
            worklog.save()
            return redirect('worklog_list')
    
    return render(request, 'log_app/add_worklog.html', {
        'form': WorkLogForm(),
        'teams': request.user.teams.all()  # Pass teams to template
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


#==================================================Team section==========================================================
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Team

@login_required
def create_team(request):
    users = User.objects.exclude(id=request.user.id).order_by('username')[:200]  # Limit to 200
    
    if request.method == 'POST':
        team = Team.objects.create(
            name=request.POST['name'],
            manager=request.user
        )
        selected_ids = request.POST.getlist('members')
        team.members.add(request.user, *selected_ids)  # Add manager + selected members
        return redirect('team_dashboard', team.id)
    
    return render(request, 'log_app/create_team.html', {
        'users': users
    })

@login_required
def team_dashboard(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.user not in team.members.all():
        raise PermissionDenied
    
    logs = WorkLog.objects.filter(team=team).order_by('-date_logged')
    members = team.members.annotate(
        total_hours=Sum('worklog__hours_spent')
    )
    
    return render(request, 'log_app/team_dashboard.html', {
        'team': team,
        'logs': logs,
        'members': members
    })


from django.http import JsonResponse
from django.core.paginator import Paginator

def user_search_api(request):
    search = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    
    users = User.objects.filter(
        Q(username__icontains=search) |
        Q(email__icontains=search)
    ).values('id', 'username', 'email')[:100]  # Limit for safety
    
    paginator = Paginator(users, 20)
    return JsonResponse({
        'results': list(paginator.page(page)),
        'has_next': paginator.page(page).has_next()
    })