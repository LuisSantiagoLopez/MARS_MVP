from django.urls import path
from . import views

urlpatterns = [
 path("chatbot", views.chatbot, name="chatbot"),
 path("", views.chatbot, name="chatbot")
]