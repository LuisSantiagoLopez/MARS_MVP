from settings.settings import openaiclient
from .find_most_recent_file import find_most_recent_file
import base64

# el vision de openai solo acepta o un url del internet o una imagen base64. 
def encode_image(image_path): 
    with open(image_path, "rb") as image_file: 
        return base64.b64encode(image_file.read()).decode('utf-8')

# esta función tiene el fin de entender el producto del usuario para poder generar una idea de publicación así como un prompt para la imagen de producto. 
def understandUserProduct(descripcion_negocio=0):
    
    most_recent_image = find_most_recent_file("functions/product_pictures/product_pictures_raw")
    
    base64_image = encode_image(most_recent_image) # convertimos el la imagen en base64

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
                # pasamos el url con el encoding 64. 
                "url": f"data:image/jpeg;base64,{base64_image}",
            },
            },
        ],
        }
    ],
    max_tokens=300,
    )

    # devolvemos respuesta del modelo
    return response.choices[0].message.content