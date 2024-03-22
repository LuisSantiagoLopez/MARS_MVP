from django.urls import path
from . import views

urlpatterns = [
    path("", views.chatbot, name="chatbot"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("chatbot/<int:session_id>/", views.chatbot, name="chatbot"),
    path("create-session/", views.chatbot, name="create_chat_session"),
    path("change-session/<int:session_id>/", views.chatbot, name="change_chat_session"),
    path("delete-session/<int:session_id>/", views.delete_session, name="delete_session"),
    path("politica-de-privacidad", views.privacy_policy, name='privacy_policy'),
    path("terminos-y-condiciones", views.terms_and_conditions, name='terms_and_conditions'),
]