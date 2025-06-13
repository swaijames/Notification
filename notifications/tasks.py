from celery import shared_task
from .models import Notification, NotificationPreference
from django.utils import timezone
import logging
import time

logger = logging.getLogger(__name__)


def should_send_notification(user, notification_type):
    """Check user preferences and DND settings"""
    try:
        pref = NotificationPreference.objects.get(user=user)
        now = timezone.now().time()

        # Check notification type enabled
        if notification_type == 'email' and not pref.email_enabled:
            return False
        elif notification_type == 'sms' and not pref.sms_enabled:
            return False
        elif notification_type == 'push' and not pref.push_enabled:
            return False

        # Check DND window
        if pref.do_not_disturb_start and pref.do_not_disturb_end:
            if pref.do_not_disturb_start <= now <= pref.do_not_disturb_end:
                return False

        return True
    except NotificationPreference.DoesNotExist:
        return True  # Default to sending if no preferences exist


@shared_task(bind=True, max_retries=3)
def process_notification(self, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.status = 'processing'
        notification.save()

        # Check user preferences
        if not should_send_notification(notification.user, notification.notification_type):
            notification.status = 'ignored'
            notification.save()
            logger.info(f"Notification {notification_id} ignored due to preferences")
            return

        # Simulate notification sending
        logger.info(
            f"\n=== SENDING {notification.notification_type.upper()} ===\n"
            f"To: {notification.user.email}\n"
            f"Subject: {notification.subject}\n"
            f"Message: {notification.message}\n"
            f"================================="
        )
        time.sleep(1)  # Simulate processing time

        # Simulate success/failure (50% failure rate for testing)
        if notification_id % 2 == 0:  # Even IDs fail
            raise Exception("Simulated provider failure")

        notification.status = 'sent'
        notification.processed_at = timezone.now()
        notification.save()

    except Exception as e:
        notification.status = 'failed'
        notification.retry_count += 1
        notification.last_retry = timezone.now()
        notification.metadata['error'] = str(e)
        notification.save()

        if notification.retry_count < 3:
            logger.warning(f"Retrying notification {notification_id} (attempt {notification.retry_count})")
            raise self.retry(countdown=2 ** notification.retry_count)
        else:
            logger.error(f"Permanent failure for notification {notification_id}: {str(e)}")
