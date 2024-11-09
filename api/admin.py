from django.contrib import admin
from .models import TelegramUser, Payment, Message

admin.site.register(TelegramUser)
admin.site.register(Payment)
admin.site.register(Message)
