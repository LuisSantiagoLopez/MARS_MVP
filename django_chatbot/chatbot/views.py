from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User 
from django.utils import timezone 
from .models import Chat
from dotenv import load_dotenv
import os
from openai import OpenAI

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

openaitoken=os.getenv('OPENAI_API_KEY')
openaiclient = OpenAI(api_key=openaitoken)

def ask_openai(message):
  model = "gpt-3.5-turbo-1106"

  response = openaiclient.chat.completions.create( # mandamos el request al api de openai
    model=model,
    messages=[
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": message},
    ]
  )

  response = response.choices[0].message.content.strip()
  return response 

def chatbot(request):
  chats = Chat.objects.filter(user=request.user)
  if request.method == 'POST':
    message = request.POST.get("message")
    response = ask_openai(message)
    chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
    chat.save()
    return JsonResponse({"message":message,"response":response})
    
  return render(request,"chatbot.html",{"chats": chats})

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