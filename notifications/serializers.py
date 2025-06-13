from rest_framework import serializers
from .models import Notification, User


# OopCompanion:suppressRename


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Notification
        fields = [
            'user',
            'notification_type',
            'subject',
            'message',
            'status',
            'metadata'
        ]
        read_only_fields = ['status', 'metadata']
