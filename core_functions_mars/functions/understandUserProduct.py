from ..settings.settings import openaiclient
from chatbot.models import Chat 
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# esta función tiene el fin de entender el producto del usuario para poder generar una idea de publicación así como un prompt para la imagen de producto. 
def understandUserProduct(chat_instance_id, conversationCostCalculator, descripcion_negocio=0):

    # Paso 1: Encontrar el usuario asociado con la instancia de chat dada
    chat_instance = Chat.objects.get(id=chat_instance_id)
    chat_session = chat_instance.chat_session

    # Paso 2: Encontrar la última imagen subida por ese usuario
    recent_chat_with_image = Chat.objects.filter(chat_session=chat_session).exclude(user_input_image='').order_by('-created_at').first()

    if recent_chat_with_image is None or not recent_chat_with_image.user_input_image:
        return "No se encontró una imagen reciente para el usuario."

    image_path = recent_chat_with_image.user_input_image.path
    base64_image = encode_image(image_path) 

    model = "gpt-4-vision-preview"

    response = openaiclient.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
        "role": "user",
        "content": [
            # Hice el prompt con el fin de que el modelo viera las capacidades mercadológicas del producto.
            {"type": "text", "text": f"""La imagen adjunta es el producto del usuario. Analiza la imagen y describe el producto. Asimismo, resalta características del producto con uso potencial mercadológico. {"Utiliza la descripción del negocio dentro de las etiquetas XML como contexto del producto <descripción negocio>{descripcion_negocio}</descripción negocio>" if descripcion_negocio != 0 else ""}"""},
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
            },
            },
        ],
        }
    ],
    max_tokens=300,
    )

    # calcula costos de vision
    conversationCostCalculator.calculate_chat_and_vision_tokens(response,model)

    # devolvemos respuesta del modelo
    return response.choices[0].message.content