from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from user_payments.models import UserPayments
from dotenv import load_dotenv
from django.contrib import messages
import stripe
import time
import os


load_dotenv()
stripe_api_key = os.getenv("STRIPE_API_KEY_TEST")

@login_required(login_url = "/login/")
def product_page(request):
  stripe.api_key = stripe_api_key
  price_id = None

  if request.method == "POST": 
      option_id = request.POST.get("option_id")
      if option_id == "1":
          price_id = "price_1Of2mbCgimrkAXdjv59KSL0K"
      if option_id == "2": 
          price_id = "price_1Of2n0CgimrkAXdjn9dXOIVO"

      checkout_session = stripe.checkout.Session.create(
          payment_method_types = ["card"],
          line_items = [
                {
                   "price": price_id,
                   "quantity": 1,
                },
            ],
           mode = "subscription",
           success_url = request.build_absolute_uri('payment_successful') + '?session_id={CHECKOUT_SESSION_ID}',
           cancel_url = request.build_absolute_uri('payment_cancelled'),
        )

      return redirect(checkout_session.url, code=303)
  
  return render(request, "user_payment/product_page.html") 

def payment_successful(request):
   stripe.api_key = stripe_api_key

   checkout_session_id = request.GET.get("session_id", None)

   user_payment = UserPayments.objects.create(app_user=request.user, stripe_checkout_id=checkout_session_id)
   user_payment.save()

   messages.add_message(request, messages.INFO, "Gracias por volverte parte de nuestra comunidad, ya puedes chatear con MARS o crear más publicaciones.")

   return redirect('/chatbot/')

def payment_cancelled(request):
   return render(request, "user_payment/payment_cancelled.html")

@csrf_exempt
def stripe_webhook(request):
   stripe.api_key = stripe_api_key
   time.sleep(10)
   payload = request.body
   signature_header = request.META["HTTP_STRIPE_SIGNATURE"]
   event = None
   try:
      event = stripe.Webhook.construct_event(payload, signature_header, stripe_api_key)
   except ValueError as e: 
      return HttpResponse(status=400)
   except stripe.error.SignatureVerificationError as e: 
      return HttpResponse(status=400) 
   
   event_type = event["type"]

   if event_type == "checkout.session.completed":
      session = event["data"]["object"]
      session_id = session.get("id")
      customer = session.get("customer")
      time.sleep(15)
      line_items = stripe.checkout.Session.list_line_items(session_id, limit=1)
      user_payment = UserPayments.objects.get(stripe_checkout_id=session_id)
      user_payment.subscription_status = True
      user_payment.stripe_customer_id = customer
      user_payment.save()
   elif event_type == 'invoice.paid':
      print(0)
   elif event_type == 'invoice.payment_failed':
      user_payment.subscription_status = False
      user_payment.save()
   else:
      print(f"Unhandled event type {event_type}")

   return HttpResponse(status=200)

@login_required(login_url = "/login/")
def customer_portal(request):

   # Retrieve the Stripe Customer ID from your database
   user_payment = UserPayments.objects.get(app_user=request.user)

   if user_payment:
      stripe.api_key = stripe_api_key

      checkout_session_id = user_payment.stripe_checkout_id
      session = stripe.checkout.Session.retrieve(checkout_session_id)
      customer = stripe.Customer.retrieve(session.customer)

      # Create a session for the Stripe Customer Portal
      session = stripe.billing_portal.Session.create(
         customer=customer,
         return_url=request.build_absolute_uri('/chatbot/'),  # Specify where the user should be redirected after leaving the portal
      )

      # Redirect the user to the Stripe Customer Portal
      return redirect(session.url)
   
   else: 
      messages.add_message(request, messages.INFO, "Todavía no has realizado un pago. Suscríbete y podrás acceder al portal de pagos, ¡gracias!")
      return redirect("/chatbot/")

@login_required(login_url = "/login/")
def settings(request): 
   user_payment = UserPayments.objects.get(app_user=request.user)

   context = {
      "user": request.user,
      "payment_plan": user_payment.payment_plan,
   }

   render(request, "settings.html")