import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_app.settings')

app = Celery('notification_app')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Windows optimization (required for Windows 10/11)
app.conf.worker_pool = 'solo'  # Use solo pool for Windows compatibility
app.conf.worker_max_tasks_per_child = 100  # Prevent memory leaks
app.conf.worker_prefetch_multiplier = 1  # Fair task distribution

# Auto-discover tasks in all Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Error email setup (optional)
app.conf.worker_send_task_events = True
app.conf.worker_hijack_root_logger = False


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
