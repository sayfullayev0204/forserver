from celery import shared_task

from api.models import TelegramUser
from functions.utils import send_telegram_message


@shared_task
def send_message_to_all_users(
    message, button_url=None, image=None, video=None, video_note=None
):
    users = TelegramUser.objects.all()
    for user in users:
        result = send_telegram_message(
            telegram_id=user.telegram_id,
            message=message,
            button_url=button_url,
            image=image if image else None,
            video=video if video else None,
            video_note=video_note if video_note else None,
        )
        if not result:
            print(
                f"Message not sent: {user.telegram_id} (user might have blocked the bot)"
            )


@shared_task
def send_message_to_non_payers(
    message, button_url=None, image=None, video=None, video_note=None
):
    users = TelegramUser.objects.all()
    for user in users:
        result = send_telegram_message(
            telegram_id=user.telegram_id,
            message=message,
            button_url=button_url,
            image=image if image else None,
            video=video if video else None,
            video_note=video_note if video_note else None,
        )
        if not result:
            print(
                f"Message not sent: {user.telegram_id} (user might have blocked the bot)"
            )


@shared_task
def send_message_to_payers(
    message, button_url=None, image=None, video=None, video_note=None
):
    users = TelegramUser.objects.filter(payment__is_confirmed=True).distinct()
    for user in users:
        result = send_telegram_message(
            telegram_id=user.telegram_id,
            message=message,
            button_url=button_url,
            image=image if image else None,
            video=video if video else None,
            video_note=video_note if video_note else None,
        )
        if not result:
            print(
                f"Message not sent: {user.telegram_id} (user might have blocked the bot)"
            )
