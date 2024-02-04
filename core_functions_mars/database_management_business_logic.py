from chatbot.models import Chat 
import json
from django.utils import timezone
from datetime import datetime 
from chatbot.models import Chat, ChatSession
from django.core.files.base import ContentFile


def save_image_to_database(responsecontent, chat_instance_id):
    chat_instance = Chat.objects.get(id=chat_instance_id)  # Obtener la instancia existente

    image_file = ContentFile(responsecontent)
    date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    image_name = f"generated_image_{date}.jpg"

    chat_instance.image_path.save(image_name, image_file)  # Actualizar la instancia con la nueva imagen
    chat_instance.save()

    return chat_instance.id

def save_database_chat_data(chat_session=None, chat_instance_id=None, user_message=None, user_input_image=None, assistant_response=None):
    chat_instance = None
    image_url = None

    if chat_instance_id is None:
        # Guardar nueva instancia con mensaje e imagen del usuario
        print("CREATING NEW INSTANCE...")
        chat_instance = Chat(chat_session=chat_session, message=user_message, user_input_image=user_input_image)
        chat_instance.save()

        return chat_instance.id
    
    else:
        print("SAVING RESPONSE TO CREATED INSTANCE")
        # Obtener instancia existente
        chat_instance = Chat.objects.get(id=chat_instance_id)

        if assistant_response:
            response_data = json.loads(assistant_response)
            chat_instance.response = response_data.get('response')

            if 'db_id' in response_data:
                # Recuperar el URL de la imagen existente en la instancia
                image_url = chat_instance.image_path.url

        chat_instance.created_at = timezone.now()
        chat_instance.save()

    return chat_instance.response, image_url

def save_chat_session(user, assistant, thread):
    new_session = ChatSession(
        user=user,
        assistant_id=assistant.id,  
        thread_id=thread.id        
    )
    new_session.save()
    return new_session.id
