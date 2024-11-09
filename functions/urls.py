from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("payment_list/", views.unconfirmed_payments, name="unconfirmed_payments"),
    path(
        "confirm_payment/<int:payment_id>/",
        views.confirm_payment,
        name="confirm_payment",
    ),
    path(
        "reject_payment/<int:payment_id>/", views.reject_payment, name="reject_payment"
    ),
    path("users/", views.user_list, name="user_list"),
    path("messages/<int:telegram_id>/", views.user_messages, name="user_messages"),
    path(
        "send-message-to-user/<int:user_id>/",
        views.send_message_to_user,
        name="send_message_to_user",
    ),
    path("tulov_qilgan/", views.tulov_qilgan, name="tulov_qilgan"),
    path("tulov_qilmagan/", views.tulov_qilmagan, name="tulov_qilmagan"),
    path("hammaga/", views.hammaga, name="hammaga"),
    path("all-users/", views.telegram_users_view, name="users_list"),
    path("sendmessage/<int:telegram_id>/", views.send_message, name="send_message"),
]
