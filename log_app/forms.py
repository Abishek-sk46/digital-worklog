from django import forms
from .models import WorkLog

class WorkLogForm(forms.ModelForm):
    hours_spent = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'step': '0.25',  # Allows .25, .50, .75, etc.
            'min': '0.1',     # Minimum 0.1 hours
            'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-400'
        })
    )


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


from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'bio']
        widgets = {
            'role': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'rows': 4
            }),
        }