from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect 
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login


def signup(request):
  if request.method == "POST": 
    form = RegisterForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect("/chatbot/")

  else:
    form = RegisterForm()
  
  return render(request, "registration/sign_up.html", {"form": form})

