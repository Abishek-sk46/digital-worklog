from django import forms
from .models import WorkLog

class WorkLogForm(forms.ModelForm):
    class Meta:
        model = WorkLog
        fields = ['task_list', 'description', 'hours_spent']



from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']