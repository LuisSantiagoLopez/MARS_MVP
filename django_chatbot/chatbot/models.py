from django.db import models
from django.contrib.auth.models import User 

# Create your models here.
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # si ya está tu usuario en ChatSessions ya no tienes que ponerlo aquí en chats 
    message = models.TextField(null=True, blank=True) 
    response = models.TextField(null=True, blank=True)
    image_path = models.ImageField(null=True, blank=True, upload_to="core_functions_mars/functions/saved_images")
    user_input_image = models.ImageField(null=True, blank=True, upload_to="core_functions_mars/functions/downloaded_images")
    created_at = models.DateField(auto_now_add=True)