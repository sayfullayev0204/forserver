from django import forms
from api.models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text", "image", "video", "url"]
