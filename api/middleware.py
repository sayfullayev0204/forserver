from django.contrib.auth import logout
from django.utils import timezone


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_login = request.user.last_login
            if (
                last_login and (timezone.now() - last_login).total_seconds() > 3600
            ):  # 1 soat
                logout(request)

        request.session.set_expiry(0)

        response = self.get_response(request)
        return response
