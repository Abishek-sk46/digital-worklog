from django.db import models
from django.contrib.auth.models import User


# Profile model to assign roles to users
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

# from myapp.todo_app.views import task_list

class WorkLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_list=models.CharField(max_length=100)
    description = models.TextField()
    hours_spent = models.FloatField()
    date_logged = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_list