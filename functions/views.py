from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from api.models import Payment,TelegramUser,Message
import requests
import json
from django.utils.timezone import now, timedelta
from django.db.models import Count,Q
from .forms import MessageForm
from django.contrib.auth.decorators import login_required


BOT_TOKEN = '7378803947:AAHqiED0UWIGg9icBpIYKAmkyiokfd6nlmg'

@login_required
def home(request):
    filter_type = request.GET.get('filter_type', 'weekly')

    users = TelegramUser.objects.all().count()+5056
    all_payments = Payment.objects.filter(is_confirmed=True).values('user').distinct().count()+435
    summa_payments = all_payments * 97000+42195000
    no_payments = users - all_payments

    today = now().date()

    if filter_type == 'monthly':
        date_range = [today - timedelta(days=i) for i in range(30)][::-1]
    else:
        date_range = [today - timedelta(days=i) for i in range(7)][::-1]

    registration_data = TelegramUser.objects.filter(
        date__range=[date_range[0], today]
    ).values('date').annotate(count=Count('id')).order_by('date')

    payment_data = Payment.objects.filter(
        user__date__range=[date_range[0], today],
        is_confirmed=True
    ).values('user__date').annotate(count=Count('id')).order_by('user__date')

    registration_counts = {data['date']: data['count'] for data in registration_data}
    payment_counts = {data['user__date']: data['count'] for data in payment_data}
    
    daily_registration = [registration_counts.get(day, 0) for day in date_range]
    daily_payments = [payment_counts.get(day, 0) for day in date_range]

    content = {
        'users': users,
        'all_payments': all_payments,
        'summa_payments': summa_payments,
        'no_payments': no_payments,
        'filter_type': filter_type,  
        'date_range': [day.strftime('%Y-%m-%d') for day in date_range],
        'daily_registration': daily_registration,
        'daily_payments': daily_payments
    }

    return render(request, 'home.html', content)



def send_message_to_user(telegram_id, message, inline_button_text=None, inline_button_url=None):
    bot_token = BOT_TOKEN
    chat_id = telegram_id
    text = message
    
    reply_markup = None
    if inline_button_text and inline_button_url:
        reply_markup = {
            "inline_keyboard": [
                [{"text": inline_button_text, "url": inline_button_url}]
            ]
        }

    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)

    response = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data=data)

    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
@login_required
def unconfirmed_payments(request):
    payments = Payment.objects.filter(is_confirmed=False)
    return render(request, 'lists.html', {'payments': payments})
@login_required
def confirm_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    first_name = payment.user.first_name
    payment.is_confirmed = True
    payment.save()
    
    send_message_to_user(
        payment.user.telegram_id,
        f"{first_name} To'lov chekingiz muvaffaqiyatli tasdiqlandi.\n\nSizga Workshop darslari uchun Yopiq Kanalimiz uchun dostup yuboryapman.\n\nPastdagi tugmani bosib yopiq kanalimizga qo'shilib oling.\n\nTez orada darslarni boshlemiz!",
        inline_button_text="YOPIQ KANALGA QO'SHILISH",
        inline_button_url="https://t.me/+tMgKG_O6n503ZmRi"  
    )
    
    messages.success(request, "To'lov tasdiqlandi.")
    return redirect('unconfirmed_payments')
@login_required
def reject_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    user = payment.user.first_name
    
    send_message_to_user(
        payment.user.telegram_id,
        f"{user}, Siz yuborgan chek tasdiqdan o'tmadi.❌\n\nIltimos, chekni tekshirib qaytadan shu yerga yuboring yoki 'Adminga yozish' tugmasini bosib, adminga yuboring!",
        inline_button_text="ADMINGA YOZISH",
        inline_button_url="https://t.me/uzumsavdogar"
        )
    
    payment.delete()
    messages.error(request, "To'lov tasdiqlanmadi")
    return redirect('unconfirmed_payments')

@login_required
def user_list(request):
    messages = Message.objects.all().select_related('user').order_by('user', '-date')

    user_messages = {}
    for message in messages:
        if message.user not in user_messages:
            user_messages[message.user] = []
        user_messages[message.user].append(message)
    
    return render(request, 'message/chats.html', {'user_messages': user_messages})

@login_required
def user_messages(request, telegram_id):
    user = get_object_or_404(TelegramUser, telegram_id=telegram_id)
    messages = Message.objects.filter(user=user).order_by('-date')

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = user
            message.save()

            send_message_to_telegram(user.telegram_id, message)

            delete_telegram_messages(user, messages)

            Message.objects.filter(user=user).delete()

            return redirect('user_list')
    else:
        form = MessageForm()

    return render(request, 'message/user_messages.html', {
        'user': user,
        'messages': messages,
        'form': form
    })

def send_message_to_telegram(telegram_id, message):
    bot_token = BOT_TOKEN 
    base_url = f"https://api.telegram.org/bot{bot_token}"

    payload = {
        'chat_id': telegram_id,
    }

    if message.text:
        payload['text'] = message.text

    if message.url:
        inline_keyboard = [[{'text': 'Visit URL', 'url': message.url}]]
        payload['reply_markup'] = {
            'inline_keyboard': inline_keyboard
        }
    
    response = requests.post(f"{base_url}/sendMessage", json=payload)
    response.raise_for_status()  
    if message.image:
        url = f"{base_url}/sendPhoto"
        files = {'photo': message.image.file}
        payload = {'chat_id': telegram_id}
        requests.post(url, data=payload, files=files)

    if message.video:
        url = f"{base_url}/sendVideo"
        files = {'video': message.video.file}
        payload = {'chat_id': telegram_id}
        requests.post(url, data=payload, files=files)

def delete_telegram_messages(user, messages):
    bot_token = BOT_TOKEN
    for message in messages:
        if message.message_id:
            url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
            payload = {
                'chat_id': user.telegram_id,
                'message_id': message.message_id
            }
            requests.post(url, data=payload)



def send_telegram_message(telegram_id, message=None, button_url=None, button_text="Open Link", image=None, video=None, video_note=None):
    url_base = f'https://api.telegram.org/bot{BOT_TOKEN}/'

    reply_markup = {}
    if button_url:
        reply_markup = {
            "inline_keyboard": [[
                {"text": button_text, "url": button_url}
            ]]
        }

    files = None 

    if image:
        url = url_base + 'sendPhoto'
        data = {
            'chat_id': telegram_id,
            'caption': message if message else '',  
            'reply_markup': json.dumps(reply_markup) if button_url else None
        }
        files = {'photo': image}
    
    elif video:
        url = url_base + 'sendVideo'
        data = {
            'chat_id': telegram_id,
            'caption': message if message else '',  
            'reply_markup': json.dumps(reply_markup) if button_url else None
        }
        files = {'video': video}

    elif video_note:
        url = url_base + 'sendVideoNote'
        data = {
            'chat_id': telegram_id,
            'reply_markup': json.dumps(reply_markup) if button_url else None
        }
        files = {'video_note': video_note}
    
    else:
        url = url_base + 'sendMessage'
        data = {
            'chat_id': telegram_id,
            'text': message,
            'reply_markup': json.dumps(reply_markup) if button_url else None
        }

    try:
        if files:
            response = requests.post(url, data=data, files=files)
        else:
            response = requests.post(url, data=data)
        
        response_data = response.json()

        # Agar foydalanuvchi botni bloklagan bo'lsa, xatoni ushlaymiz
        if response.status_code == 403:
            print(f"Foydalanuvchi {telegram_id} botni bloklagan.")
            return False  # Bot bloklanganligini bildiradi

        return response_data

    except Exception as e:
        print(f"Xato yuz berdi: {e}")
        return False  # Har qanday xatolikda qaytaradi


@login_required
def tulov_qilgan(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        button_url = request.POST.get('url')
        image = request.FILES.get('image')  
        video = request.FILES.get('video')  
        video_note = request.FILES.get('video_note')  
        users = TelegramUser.objects.filter(payment__is_confirmed=True).distinct()

        if users.exists():
            for user in users:
                result = send_telegram_message(
                    telegram_id=user.telegram_id,
                    message=message,
                    button_url=button_url,
                    image=image if image else None,
                    video=video if video else None,
                    video_note=video_note if video_note else None
                )
                if not result:
                    print(f"Xabar yuborilmadi: {user.telegram_id} (foydalanuvchi botni bloklagan bo'lishi mumkin)")

            messages.success(request, f"Xabar to'lov qilgan foydalanuvchilarga yuborildi!")
        else:
            messages.warning(request, "No users found who have made payment.")

        return redirect('tulov_qilgan')

    return render(request, 'message/send.html', {'title': "To'lov qilgan foydalanuvchilar"})


@login_required
def tulov_qilmagan(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        button_url = request.POST.get('url')
        image = request.FILES.get('image')  
        video = request.FILES.get('video')  
        video_note = request.FILES.get('video_note')  
        users = TelegramUser.objects.all()
        
        if users.exists():
            for user in users:
                result = send_telegram_message(
                    telegram_id=user.telegram_id,
                    message=message,
                    button_url=button_url,
                    image=image if image else None,
                    video=video if video else None,
                    video_note=video_note if video_note else None
                )
                if not result:
                    print(f"Xabar yuborilmadi: {user.telegram_id} (foydalanuvchi botni bloklagan bo'lishi mumkin)")

            messages.success(request, f"Xabar to'lov qilmagan foydalanuvchilarga yuborildi!")
        else:
            messages.warning(request, "To'lov qilmagan foydalanuvchilar topilmadi.")

        return redirect('tulov_qilmagan')

    return render(request, 'message/send.html', {'title': "To'lov qilmagan foydalanuvchilar"})

@login_required
def hammaga(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        button_url = request.POST.get('url')
        image = request.FILES.get('image')  
        video = request.FILES.get('video')  
        video_note = request.FILES.get('video_note')  
        users = TelegramUser.objects.all()

        if users.exists():
            for user in users:
                result = send_telegram_message(
                    telegram_id=user.telegram_id,
                    message=message,
                    button_url=button_url,
                    image=image if image else None,
                    video=video if video else None,
                    video_note=video_note if video_note else None
                )
                if not result:
                    print(f"Xabar yuborilmadi: {user.telegram_id} (foydalanuvchi botni bloklagan bo'lishi mumkin)")

            messages.success(request, f"Xabar barcha foydalanuvchilarga yuborildi!")
        else:
            messages.warning(request, "No users found.")

        return redirect('hammaga')

    return render(request, 'message/send.html', {'title': "Barcha foydalanuvchilar"})


TOKEN = BOT_TOKEN

def telegram_users_view(request):
    users = TelegramUser.objects.all()
    users_with_payment_status = []
    
    for user in users:
        # Foydalanuvchining tasdiqlangan to'lovlarini tekshiramiz
        has_payment = Payment.objects.filter(user=user, is_confirmed=True).exists()
        users_with_payment_status.append({
            'user': user,
            'has_payment': has_payment
        })
    
    context = {
        'payments': users_with_payment_status
    }
    
    return render(request, 'message/list.html', context)

def send_message(request, telegram_id):
    try:
        telegram_user = TelegramUser.objects.get(telegram_id=telegram_id)
    except TelegramUser.DoesNotExist:
        telegram_user = None
        messages.error(request, "Telegram foydalanuvchisi topilmadi.")
        return redirect('users_list')
    if request.method == 'POST':
        text = request.POST.get('text')
        image = request.FILES.get('image')
        url = request.POST.get('url')

        if image and text and url:
            keyboard = {
                'inline_keyboard': [[{'text': "Havolaga o'tish", 'url': url}]]
            }

            files = {'photo': image}
            image_data = {
                'chat_id': telegram_id,
                'caption': text,
                'parse_mode': 'HTML',
                'reply_markup': json.dumps(keyboard)
            }

            response = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data=image_data, files=files)

            if response.status_code == 200:
                messages.success(request, "Xabar muvaffaqiyatli yuborildi!")
            else:
                messages.error(request, f"Xato yuz berdi: {response.content}")

        elif text and url:
            data = {
                'chat_id': telegram_id,
                'text': text,
                'parse_mode': 'HTML',
                'reply_markup': json.dumps({
                    'inline_keyboard': [[{'text': "Havolaga o'tish", 'url': url}]]
                })
            }
            response = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=data)

            if response.status_code == 200:
                messages.success(request, "Matn va URL muvaffaqiyatli yuborildi!")
            else:
                messages.error(request, f"Xato yuz berdi: {response.content}")

        elif image and text:
            files = {'photo': image}
            image_data = {
                'chat_id': telegram_id,
                'caption': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data=image_data, files=files)

            if response.status_code == 200:
                messages.success(request, "Rasm va matn muvaffaqiyatli yuborildi!")
            else:
                messages.error(request, f"Xato yuz berdi: {response.content}")

        elif text:
            data = {
                'chat_id': telegram_id,
                'text': text,
                'parse_mode': 'HTML',
            }
            response = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=data)

            if response.status_code == 200:
                messages.success(request, "Matn muvaffaqiyatli yuborildi!")
            else:
                messages.error(request, f"Xato yuz berdi: {response.content}")

        return redirect('users_list')

    return render(request, 'message/chat.html', {'telegram_id': telegram_id, 'telegram_user':telegram_user})
