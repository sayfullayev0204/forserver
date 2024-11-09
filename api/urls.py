from django.urls import path
from . import views

urlpatterns = [
    path("users/<int:telegram_id>/", views.telegram_user_view),
    path("users/", views.telegram_user_view),
    path("payments/<int:telegram_id>/", views.payment_detail, name="payment_detail"),
    path("payment/<int:telegram_id>/", views.save_payment, name="save_payment"),
    path("messages/<int:telegram_id>/", views.save_message),
    path(
        "change-login-password/",
        views.change_login_password,
        name="change_login_password",
    ),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("export-users/", views.export_users_to_excel, name="export_users_to_excel"),
]
