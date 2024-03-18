from ..settings.settings import openaiclient
from chatbot.models import Chat 
import base64
import logging 

logger = logging.getLogger('application')

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    logger.info(f"Image at {image_path} encoded successfully.")
    return encoded_image

# esta función tiene el fin de entender el producto del usuario para poder generar una idea de publicación así como un prompt para la imagen de producto. 
def understandUserProduct(chat_instance_id, conversationCostCalculator, descripcion_negocio=0):
    logger.info(f"Starting process to understand user product with chat_instance_id: {chat_instance_id} and descripcion_negocio: {descripcion_negocio}")

    # Paso 1: Encontrar el usuario asociado con la instancia de chat dada
    chat_instance = Chat.objects.get(id=chat_instance_id)
    chat_session = chat_instance.chat_session
    logger.info(f"Chat instance with ID {chat_instance_id} found, associated chat session: {chat_session}")

    # Paso 2: Encontrar la última imagen subida por ese usuario
    recent_chat_with_image = Chat.objects.filter(chat_session=chat_session).exclude(user_input_image='').order_by('-created_at').first()

    if recent_chat_with_image is None or not recent_chat_with_image.user_input_image:
        logger.warning(f"No recent image found for chat session: {chat_session}")
        return "No se encontró una imagen reciente para el usuario."

    image_path = recent_chat_with_image.user_input_image.path
    logger.info(f"Recent image found at path: {image_path}")
    base64_image = encode_image(image_path) 

    model = "gpt-4-vision-preview"
    logger.info(f"Using model {model} for generating product description")

    response = openaiclient.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
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

    logger.info(f"OpenAI completion request sent for chat session: {chat_session}")

    # calcula costos de vision
    conversationCostCalculator.calculate_chat_and_vision_tokens(response, model)
    logger.info("Conversation and vision tokens cost calculated.")

    # devolvemos respuesta del modelo
    model_response = response.choices[0].message.content
    logger.info(f"Model response obtained: {model_response}")
    return model_response