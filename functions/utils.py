import json

import requests

BOT_TOKEN = "7378803947:AAHqiED0UWIGg9icBpIYKAmkyiokfd6nlmg"


def send_telegram_message(
    telegram_id,
    message=None,
    button_url=None,
    button_text="Open Link",
    image=None,
    video=None,
    video_note=None,
):
    url_base = f"https://api.telegram.org/bot{BOT_TOKEN}/"

    reply_markup = {}
    if button_url:
        reply_markup = {"inline_keyboard": [[{"text": button_text, "url": button_url}]]}

    files = None

    if image:
        url = url_base + "sendPhoto"
        data = {
            "chat_id": telegram_id,
            "caption": message if message else "",
            "reply_markup": json.dumps(reply_markup) if button_url else None,
        }
        files = {"photo": image}

    elif video:
        url = url_base + "sendVideo"
        data = {
            "chat_id": telegram_id,
            "caption": message if message else "",
            "reply_markup": json.dumps(reply_markup) if button_url else None,
        }
        files = {"video": video}

    elif video_note:
        url = url_base + "sendVideoNote"
        data = {
            "chat_id": telegram_id,
            "reply_markup": json.dumps(reply_markup) if button_url else None,
        }
        files = {"video_note": video_note}

    else:
        url = url_base + "sendMessage"
        data = {
            "chat_id": telegram_id,
            "text": message,
            "reply_markup": json.dumps(reply_markup) if button_url else None,
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
