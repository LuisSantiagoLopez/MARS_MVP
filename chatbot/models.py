from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assistant_id = models.CharField(max_length=255, null=True, blank=True)
    thread_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ChatSession {self.id} - User {self.user.username}"

# Create your models here.
class Chat(models.Model):
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='chats')
    message = models.TextField(null=True, blank=True) 
    response = models.TextField(null=True, blank=True)
    image_path = models.ImageField(null=True, blank=True, upload_to="saved_images")
    user_input_image = models.ImageField(null=True, blank=True, upload_to="downloaded_images")
    created_at = models.DateField(auto_now_add=True)