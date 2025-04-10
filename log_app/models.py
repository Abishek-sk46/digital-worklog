from django.db import models
from django.contrib.auth.models import User

# from myapp.todo_app.views import task_list

class WorkLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_list=models.CharField(max_length=100)
    description = models.TextField()
    hours_spent = models.FloatField()
    date_logged = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_list