from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TelegramUser, Payment
from .serializers import TelegramUserSerializer, PaymentSerializer, MessageSerializer
from .forms import ChangeLoginPasswordForm, AuthenticationForm
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from openpyxl import Workbook
from django.utils import timezone


@api_view(["GET", "POST"])
def telegram_user_view(request, telegram_id=None):
    if request.method == "GET":
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
            serializer = TelegramUserSerializer(user)
            return Response(serializer.data)
        except TelegramUser.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

    elif request.method == "POST":
        serializer = TelegramUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["POST"])
def save_payment(request, telegram_id):
    try:
        user = TelegramUser.objects.get(telegram_id=telegram_id)
        data = request.data.copy()
        data["user"] = user.id
        serializer = PaymentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    except TelegramUser.DoesNotExist:
        return Response(status=404)


@api_view(["POST"])
def save_message(request, telegram_id):
    try:
        user = TelegramUser.objects.get(telegram_id=telegram_id)
        data = request.data.copy()
        data["user"] = user.id
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    except TelegramUser.DoesNotExist:
        return Response(status=404)


@api_view(["GET", "POST"])
def payment_detail(request, telegram_id):
    try:
        user = TelegramUser.objects.get(telegram_id=telegram_id)
    except TelegramUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        # Check if the user has a payment
        try:
            payment = Payment.objects.get(user=user)
        except Payment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        # Save a new payment
        data = request.data.copy()
        data["user"] = user.id  # Associate the payment with the user

        serializer = PaymentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
def change_login_password(request):
    user = request.user
    if request.method == "POST":
        form = ChangeLoginPasswordForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Login va Parol o'zgartrildi!")
            return redirect("home")
        else:
            messages.error(request, "Xatolik ro'y berdi qayta urunub ko'ring.")
    else:
        form = ChangeLoginPasswordForm(instance=user)

    return render(request, "accounts/edit.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"{username} tizimga kirdingiz!")
                return redirect("home")
            else:
                messages.error(request, "username yoki password xato .")
        else:
            messages.error(request, "username yoki password xato .")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect("login")


def export_users_to_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Users"

    headers = ["Ism", "Telefon", "Username", "Sana", "Status"]
    ws.append(headers)

    users = TelegramUser.objects.all()
    for user in users:
        payment = Payment.objects.filter(user=user, is_confirmed=True).exists()
        payment_status = "To'lov qilingan" if payment else "To'lov qilmagan"

        ws.append(
            [user.first_name, user.phone, user.username, user.date, payment_status]
        )

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f"attachment; filename=users_{timezone.now().date()}.xlsx"
    )

    wb.save(response)
    return response
