from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Chat
from core_functions_mars.chat import Assistant
from django.conf import settings
from django.contrib.auth.decorators import login_required
import json 

# Initialize the Assistant
assistant = Assistant()

@login_required(login_url="/login/")
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get("message")
        user_input_image = request.FILES.get('image')

        if user_input_image:
            chat_image = Chat(user=request.user, user_input_image=user_input_image)
            chat_image.save()
            print(user_input_image)
            print("THE IMAGE THE USER UPLOADED WAS SAVED")

        data = json.loads(assistant.generate_assistant_response(message, request.user))

        print(data)

        response = data['response']
        instance_id = data.get('db_id', None)

        if instance_id is not None:
            instance_id = int(instance_id)
            chat = Chat.objects.get(id=instance_id)
            image_path_url = chat.image_path.url
            print("IMAGE PATH URL: " + image_path_url)
        
        else:
            chat = Chat(user=request.user)
            image_path_url = None

        chat.message = message
        chat.response = response
        chat.created_at = timezone.now()

        chat.save()
        return JsonResponse({"message": message, "response": response, "image_path_url": image_path_url})

    return render(request, "chatbot.html", {"chats": chats})