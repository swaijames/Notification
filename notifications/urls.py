# notification_system/urls.py
from django.urls import path
from .views import NotificationAPI

urlpatterns = [
    path('notify/', NotificationAPI.as_view()),
]
