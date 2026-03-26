from django.urls import path

from whatsapp.views import webhook

urlpatterns = [
    path("webhook/", webhook, name="whatsapp-webhook"),
]
