from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from user_payments.models import UserPayments
from dotenv import load_dotenv
from django.contrib import messages
import stripe
import logging
import os


load_dotenv()
stripe_api_key = os.getenv("STRIPE_API_KEY_TEST")
logger = logging.getLogger('application')

@login_required(login_url = "/login/")
#API ENDPOINT FOR THE FRONTEND'S MODAL
def product_page(request):
  if request.method == "POST":

      stripe.api_key = stripe_api_key
      option_id = request.POST.get("option_id")
      if option_id == "1":
          price_id = "price_1Of2mbCgimrkAXdjv59KSL0K"
      if option_id == "2": 
          price_id = "price_1Of2n0CgimrkAXdjn9dXOIVO"


      #CHECKOUT SESSION FROM STRIPE'S API ENDPOINTS. REDIRECTION TO STRIPE'S URL NECESSARY AFTER CREATING THE SESSION. 
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

      #SENDING THIS OBJECT TO STRIPE'S URL WITH A REQUEST THAT CONTAINS THE PAYLOAD WE JUST CREATED WITH THE PRICE ID OF THE PRODUCT 
      return redirect(checkout_session.url, code=303)

#IF THE PAYMENT WAS SUCCESSFUL THEY'LL GET REDIRECTED TO THIS VIEW AS PER STRIPE CALL. 
#API CALL FROM STRIPE
def payment_successful(request):
   stripe.api_key = stripe_api_key

   logger.debug("Payment successful")

   #INSTEAD OF SENDING THE USER TO AN ADDITIONAL WEBSITE, WE'LL REDRECT THEM TO THE CHATBOT WITH A MESSAGE THAT IS ALSO EMBEDDED INSIDE THE CHATBOT.HTML TEMPLATE
   messages.add_message(request, messages.INFO, "Gracias por volverte parte de nuestra comunidad, ya puedes chatear con MARS o crear más publicaciones.")
   return redirect('/chatbot/')

#INSTEAD OF GOING FORWARD WITH THE PAYMENT, THE PAYMENT GOT CANCELLED
#API CALL FROM STRIPE
def payment_cancelled(request):
   messages.add_message(request, messages.INFO, "Ocurrió un error con su tarjeta. Si necesita asistencia, contáctenos.")
   return redirect('/chatbot/')

@csrf_exempt
#API ENDPOINT STRIPE CALLS 
def stripe_webhook(request):
   logger.debug("Received stripe webhook call")
   #SENDING A REQUEST TO THE STRIPE WEBHOOK FOR INTERNAL PROCESSING
   webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
   payload = request.body
   signature_header = request.META["HTTP_STRIPE_SIGNATURE"]
   event = None

   #CONNECTION TO THE STRIPE WEBHOOK ENDPOINT WITH OUR STRIPE WEBHOOK SECRET
   try:
      event = stripe.Webhook.construct_event(payload, signature_header, webhook_secret)
      logger.debug(f"Stripe event: {event}")

   #EXCEPTION HANDLING
   except ValueError as e: 
      #INVALID PAYLOAD
      logger.debug(f"No event, some unknown error ocurred")
      return HttpResponse(status=400)
   except stripe.error.SignatureVerificationError as e: 
      #INVALID SIGNATURE
      logger.debug(f"No event, signature verification error {event}")
      return HttpResponse(status=400)
   
   ## EVENT HANDLING ##
   event_type = event["type"]
   #EXTRACTING THE EVENT OBJECT
   subscription = event["data"]["object"]
   stripe_subscription_id = subscription.get("id")
   subscription_number = subscription.get("subscription")
   customer = subscription.get("customer")

   logger.debug(f"INFO EVENT: Type {event_type}, type of event_type {type(event_type)}, checkout id {stripe_subscription_id}, customer {customer}, subscription number {subscription_number}")

   #MONTHLY INVOICE TO THE USER AFTER PAYMENT OR IF PAYMENT FAILED.
   if event_type in ['invoice.paid', 'invoice.payment_failed']:
      #EXTRACTING THE USER PAYMENT INSTANCE FROM THE DATBASE
      user_payment = UserPayments.objects.get(stripe_subscription_id=stripe_subscription_id)

      #CHANGING STATUS OF SUBSCRIPTION WHICH THEN BLOCKS MESSAGE SENT IN CHATBOT/VIEWS
      if event_type == 'invoice.paid':
            #NOW WE DELETE ANY OTHER PREVIOUS SUBSCRIPTION THE USER HAD 
            check_subscription = UserPayments.objects.filter(app_user=request.user, subscription_status=True).last()

            if check_subscription:
               subscription_number_previous = check_subscription.subscription_number
               stripe.Subscription.delete(subscription_number_previous)
               check_subscription.subscription_status = False
                  
            #NO USE CASE YET, BUT NICE TO HAVE THE ITEMS LISTED IN A DATA STRUCTURE
            line_items = stripe.checkout.Session.list_line_items(stripe_subscription_id, limit=1)

            #CODE OF THE SUBSCRIPTION NUMBER THEY CHOSE 
            subscription_id_bought = line_items.data[0].price.product

            logger.debug(f"SUB ID: {subscription_id_bought}")
                  
            #VERIFYING IF THE REQUEST WAS SUCCESSFUL
            user_payment = UserPayments.objects.create(app_user=request.user, stripe_subscription_id=stripe_subscription_id, stripe_customer=customer, subscription_type=subscription_id_bought, subscription_status=True, subscription_number=subscription_number)
            user_payment.save()

            logger.debug(f"Invoice paid successfully.")
            
      elif event_type == 'invoice.payment_failed':
            check_subscription = UserPayments.objects.filter(app_user=request.user, subscription_status=True).last()

            check_subscription.subscription_status = False

   #IF THE SUBSCRIPTION ENDS BECAUSE THE USER CANCELLED, WE WILL ALSO STOP PROVIDING ACCESS TO THE PLATFORM. STRIPE COLLECTS DATA. 
   elif event_type == 'customer.subscription.deleted':
      user_payment = UserPayments.objects.get(stripe_subscription_id=stripe_subscription_id)

      #CANCEL THEIR SUBSCRIPTION AND STOP GIVING THEM ACCESS 
      user_payment.subscription_status = False
      user_payment.save()

      logger.debug(f"Subscription deleted successfully")

   #RARE - IF THE WEBHOOK ISN'T FOUND, WE WON'T HANDLE IT. 
   else:
      print(f"Unhandled event type {event_type}")

   return HttpResponse(status=200)

@login_required(login_url = "/login/")
# THE CUSTOMER PORTAL FOR CANCELLATIONS, API CALL TO STRIPE.
def customer_portal(request):

   #WE TAKE THE LAST INSTANCE FROM THAT USER. 
   payment_instance = UserPayments.objects.filter(app_user=request.user).order_by("-created_at").first()

   #WE PASS THE DATBASE DATA TO STRIPE AND CALL THEIR URL 
   if payment_instance:
      stripe.api_key = stripe_api_key

      stripe_subscription_id = payment_instance.stripe_subscription_id
      session = stripe.checkout.Session.retrieve(stripe_subscription_id)
      customer = stripe.Customer.retrieve(session.customer)

      #CREATE SESSION FOR STRIPE'S PORTAL URL ENDPOINT. USERS RETURN TO CHATBOT AFTER THEY FINISH.
      session = stripe.billing_portal.Session.create(
         customer=customer,
         return_url=request.build_absolute_uri('/chatbot/'), 
      )

      #REDIRECT THE USER TO STRIPE'S URL. 
      return redirect(session.url)
   
   #IF USER HASN'T PAID THEY CAN'T PROCEED.
   else: 
      messages.add_message(request, messages.INFO, "Todavía no has realizado un pago. Suscríbete y podrás acceder al portal de pagos, ¡gracias!")
      return redirect("/chatbot/")

### IMPORTANT: HANDLE THIS SETTINGS PAGE AS AN API CALL THROUGH THE CHATBOT TEMPLATE
@login_required(login_url = "/login/")
def settings(request): 
   user_payment = UserPayments.objects.get(app_user=request.user)

   context = {
      "user": request.user,
      "payment_plan": user_payment.payment_plan,
   }

   render(request, "settings.html")
