from ..settings.settings import openaiclient, photoroomtoken
import requests
import ast
from ..database_management_business_logic import save_image_to_database
from chatbot.models import Chat


# esta función es la que produce una imagen de producto aceptable a partir de una mala imagen de producto.  
def create_product_image(prompt, chat_instance_id, conversationCostCalculator): 
    
    # Paso 1: Encontrar el usuario asociado con la instancia de chat dada
    chat_instance = Chat.objects.get(id=chat_instance_id)
    chat_session = chat_instance.chat_session

    # Paso 2: Encontrar la última imagen subida por ese usuario
    recent_chat_with_image = Chat.objects.filter(chat_session=chat_session).exclude(user_input_image='').order_by('-created_at').first()

    image_path = recent_chat_with_image.user_input_image.path
    
    if image_path is None:
        return "No se puede crear una foto de producto porque el usuario no ha subido una foto."

    url = "https://beta-sdk.photoroom.com/v1/instant-backgrounds" # el endpoint para generar imágenes de calidad

    headers = { # los headers del endpoint 
        'Accept': 'image/png, application/json',
        'x-api-key': photoroomtoken
    }
    

    files = { # el documento que contiene la imagen
        'imageFile': open(f'{image_path}', 'rb') 
    }

    data = { # el prompt sobre el que estará puesto el producto
        'prompt': prompt
    }

    response = requests.post(url, headers = headers, files = files, data = data) # el post request al endpoint

    if response.status_code == 200: # si el estatus de la llamada es igual a 200, entonces seguimos
        # Calcular costos de generar imagen con lightroom
        conversationCostCalculator.image_generation_costs("photoroom")

        instance_id = save_image_to_database(response.content, chat_instance_id)

        instance_id_string = f'''Este es el id de la imagen dentro de la base de datos, inclúyela en tu texto como db_id: "{instance_id}" '''
        print(instance_id_string)

        return instance_id_string

    else: # si no es 200 marcamos error 
        print("Error:", response.status_code, response.text)
        return 0

# esta es la función original para crear imágenes. El punto es que el modelo ya haya produdido una idea que le mandará aquí como referencia para crear la imagen. 
def generateInstagramImage(idea, chat_instance_id, conversationCostCalculator, descripcion_negocio=0, estilo=0, es_de_producto=0, feedback=0):
  
  if es_de_producto != 0:
    es_de_producto = ast.literal_eval(es_de_producto)

  if es_de_producto == True: # si la publicación es de producto, entonces empleamos photoroom para crear la nueva imagen. 
    prompt = f"""Your task is to generate a prompt for a specific type of diffusion model that replaces background images for products. The image your prompt will produce will be used as an instagram post for the idea inside XML tags. Your prompt must summerise the elements of the idea into a simple stable-diffusion style prompt with the following structure: the product on the image on the scenery or background. Do not include the XML tags in your response.
    <idea>{idea}<idea/>
    {"<descripción_negocio>{descripcion_negocio}</descripción_negocio>" if descripcion_negocio !=0 else ""}
    {"<feedback previo del usuario>{feedback}</feedback previo del usuario>" if feedback !=0 else ""}
    {"<estilo>{estilo}</estilo>" if estilo!=0 else ""}
    """

    model = "gpt-4-1106-preview"

    response = openaiclient.chat.completions.create( # mandamos el request al api de openai
    model=model,
    messages=[
      {"role": "system", "content": "Your job is to create prompts for diffusion models that create product images."},
      {"role": "user", "content": prompt},
    ]
  )

    if response:
      # Calcular costos de gpt4
      conversationCostCalculator.calculate_chat_and_vision_tokens(response,model)
      response = response.choices[0].message.content
      product_pic_path = create_product_image(response, chat_instance_id, conversationCostCalculator)
      return product_pic_path 

  else: # si no es de producto 
    prompt = f"""Tu tarea es generar una imagen con base a la idea dentro de las etiquetas XML. La imagen debe representar la idea de modo creativo. Nunca sugieras o utilices texto en las imágenes. 
    <idea>{idea}<idea/>
    {"<descripción_negocio>{descripcion_negocio}</descripción_negocio>" if descripcion_negocio !=0 else ""}
    {"<feedback previo del usuario>{feedback}</feedback previo del usuario>" if feedback !=0 else ""}
    {"<estilo>{estilo}</estilo>" if estilo!=0 else ""}
    """

    model = "dall-e-3"

    image_response = openaiclient.images.generate( # dejamos que dalle produzca el prompt y la imagen 
      model="dall-e-3",
      prompt=f"{prompt}",
      n=1,
      size="1024x1024"
    )

    print(image_response)

    # Calcular costos de gpt4
    conversationCostCalculator.image_generation_costs(model)

    image_response_url = image_response.data[0].url
    print(image_response_url)
    response = requests.get(image_response_url)

    instance_id = save_image_to_database(response.content, chat_instance_id)
    instance_id_string = f"Este es el id de la imagen que debes introducir bajo de la clave db_id en tu respuesta: {instance_id}"

    print(instance_id_string)

    return instance_id_string