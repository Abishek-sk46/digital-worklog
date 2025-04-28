from django.db import models
from django.contrib.auth.models import User

# 1. PROFILE MODEL (Unchanged)
class Profile(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# 2. NEW TEAM MODEL (Add this)
class Team(models.Model):
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='managed_teams'
    )
    members = models.ManyToManyField(
        User,
        related_name='teams'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 3. UPDATED WORKLOG MODEL (Modify existing)
class WorkLog(models.Model):
    # Existing fields (preserved)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_list = models.CharField(max_length=100)
    description = models.TextField()
    hours_spent = models.FloatField()
    date_logged = models.DateTimeField(auto_now_add=True)
    
    # New fields (added)
    team = models.ForeignKey(
        Team,
        null=True,       # Allows personal logs (team=None)
        blank=True,
        on_delete=models.SET_NULL,
        related_name='worklogs'
    )
    VISIBILITY_CHOICES = [
        ('PRIVATE', 'Only Me'),
        ('TEAM', 'Team Members'),
        ('PUBLIC', 'Everyone')
    ]
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='PRIVATE'
    )

    def __str__(self):
        return f"{self.team.name + ' | ' if self.team else ''}{self.task_list}"