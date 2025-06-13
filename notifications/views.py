from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer
from .tasks import process_notification


# OopCompanion:suppressRename


class NotificationAPI(APIView):
    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            # Create notification in pending state
            notification = serializer.save(status='pending')

            # Queue processing task
            process_notification.delay(notification.id)

            return Response({
                "id": notification.id,
                "status": "queued",
                "details": "Notification is being processed"
            }, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
