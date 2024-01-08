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

@login_required
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get("message")

        # Use the Assistant to get a response
        data = json.loads(assistant.generate_assistant_response(message))

        print(data)

        response = data['response']
        instance_id = data.get('db_id', None)

        if instance_id is not None:
            instance_id = int(instance_id)
            chat = Chat.objects.get(id=instance_id)
            chat.user = request.user
            chat.message = message
            chat.response = response
            chat.created_at = timezone.now()
            chat.save()

            image_path_url = chat.image_path.url

            print("IMAGE PATH URL: " + image_path_url)
        
        else:
            chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
            chat.save()

            image_path_url = None

        """
        image_path = data.get('image_path', None)
    
        print(image_path)

        # Save and respond with the generated response
        chat = Chat(user=request.user, message=message, response=response, image_path=image_path, created_at=timezone.now())
        chat.save()
        """

        return JsonResponse({"message": message, "response": response, "image_path_url": image_path_url})

    return render(request, "chatbot.html", {"chats": chats})

def login(request):
  if request.method == "POST":
    username = request.POST["username"]
    password = request.POST["password"]
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
      auth.login(request, user)
      return redirect("chatbot")
    else:
      error_message = "Invalid username and password"
      return render(request, "login.html", {"error_message": error_message})
  else:
    return render(request,"login.html")

def register(request):
  if request.method == "POST": 
    username = request.POST["username"]
    email = request.POST["email"]
    password1 = request.POST["password1"]
    password2 = request.POST["password2"]

    if password1 == password2:
      try:
        user = User.objects.create_user(username, email, password1)
        user.save()
        auth.login(request, user)
        return redirect("chatbot")
      except:
        error_message = "Error creating account."
        return render(request, "register.html", {"error_message": error_message})
    else:
      error_message = "Passwords don't match, try again."
      return render(request, "register.html", {"error_message": error_message})

  return render(request,"register.html")

def logout(request):
  auth.logout(request)
  return redirect("login")