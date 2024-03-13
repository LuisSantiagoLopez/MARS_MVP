from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Chat, ChatSession
from core_functions_mars.chat import Assistant
from django.contrib.auth.decorators import login_required
from user_payments.models import UserPayments, CostPerUser
from django.contrib import messages


@login_required(login_url = "/login/")
def chatbot(request, session_id=None):
    """
    Esta view tiene varias funciones. Primero, le hace render al template chatbot.html, que maneja la interacción principal con el usuario. Con el primer render, o "GET" request, pasa el id de la sesión actual, los chats de la sesión actual, y todas las sesiones de chat del usuario. 

    Si el request lo hacen junto con una sesión de chat, inicio un asistente pre-existente y extraigo sus datos de chat y de sesión, sino viene con sesión de chat creo uno nuevo. 

    Esta view también maneja la interacción con el asistente. Si chatbot.html manda un "POST" request a esta view, entonces extraigo los datos del mensaje y los mando a la clase de Assistant a procesar, dentro del módulo de chat. 

    Todo el manejo de la base de datos ocurre o 1) de una llama desde el módulo de chat, o 2) desde una de las funciones del asistente. Esta view no guarda en la base de datos. 
    """

    # Extraigo el usuario
    user = request.user

    subscription_name = ""
    current_subscription = UserPayments.objects.filter(app_user=user).order_by("-created_at").first()
    if current_subscription:
        subscription_name = current_subscription.subscription_name

    current_payments = CostPerUser.objects.filter(user=user).order_by("-timestamp").first()
    available_cost = current_payments.available_cost

    # Filtro de todas las sesiones para mostrarlas en el frontend 
    all_chat_sessions = ChatSession.objects.filter(user=user)
    # Inicio historial de chats vacío por si la conversación no tiene chats 
    chat_history_chat_session = Chat.objects.none()

    if session_id:
        # Si existe una sesión dentro del url que regresó el front-end, inicio el asistente existente
        assistant = Assistant(user, chat_session_id=session_id)
        # Encuentro la sesión conectada a la sesión activa 
        current_session = ChatSession.objects.get(id=session_id, user=user)
        # Extraigo los chats de la sesión para regresarlos al front-end
        chat_history_chat_session = Chat.objects.filter(chat_session=current_session)

    else:
        # Si no existe una sesión activa, inicio session_id como None inicialmente
        session_id = None
        # Creo un nuevo asistente y le paso el usuario como ancla 
        assistant = Assistant(user)

    # Si el tipo de request es "POST", interactúo con la clase assistants para responder
    if request.method == "POST":

        if available_cost <= 0:
            current_payments.subscription_status = False
            current_payments.save()
            messages.add_message(request, messages.INFO, "Se te acabaron los créditos, adquiere más para continuar tu uso.")
            return redirect("/chatbot/")

        if not current_subscription or current_subscription.subscription_status == False: 
            messages.add_message(request, messages.INFO, "Estamos en fase beta, por lo que las funciones actuales son pagadas. ¿Estás listo para invertir en tu marketing y crecer en redes sociales? Presiona en tu perfil en la esquina inferior izquierda y selecciona 'Mi Plan'.")
            return redirect("/chatbot/")

        # Extraigo el texto y la posible imagen que el usuario mandó
        user_message = request.POST.get("message")
        user_input_image = request.FILES.get('image', None)

        # Creo una respuesta 
        assistant_response_text, generated_image_path_url = assistant.generate_assistant_response(user_message=user_message, user_input_image=user_input_image)

        # Armo el JSON que recibirá el frontend 
        context = {
        "message": user_message,
        "response": assistant_response_text, 
        "image_path_url": generated_image_path_url,
        "session_id": assistant.chat_session_id,
        }
        
        return JsonResponse(context)
    
    else:
        # En el caso en el que el usuario mande un get request, regreso la sesión, los chats y las sesiones de chat.
        context = {
            "available_cost": available_cost,
            "subscription_name" : subscription_name,
            "session_id": session_id,
            "chats": chat_history_chat_session,
            "chat_sessions": all_chat_sessions,
        }

        return render(request, "chatbot.html", context)
    
def delete_session(request, session_id):
    if request.method == 'DELETE':
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            session.delete()
            return JsonResponse({'status': 'success'}, status=200)
        except ChatSession.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)