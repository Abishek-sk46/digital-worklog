from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from log_app.models import WorkLog

class ManagerPermissionTest(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user('manager1')
        self.manager.profile.role = 'manager'
        self.other_user_log = WorkLog.objects.create(user=User.objects.create_user('user2'), hours_spent=2)

    def test_cant_edit_others_logs(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('edit_worklog', args=[self.other_user_log.pk]))
        self.assertEqual(response.status_code, 403)