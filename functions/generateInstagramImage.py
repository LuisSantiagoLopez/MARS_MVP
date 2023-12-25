from settings.settings import openaiclient, photoroomtoken
from cost_analysis.cost_analyzer import conversationCostCalculator
from .find_most_recent_file import find_most_recent_file
import requests
import base64
import os
import ast
from datetime import datetime 

# esta función es la que produce una imagen de producto aceptable a partir de una mala imagen de producto.  
def create_product_image(prompt): 
    
    relative_image_path = find_most_recent_file("functions/product_pictures/product_pictures_raw/")

    url = "https://beta-sdk.photoroom.com/v1/instant-backgrounds" # el endpoint para generar imágenes de calidad

    headers = { # los headers del endpoint 
        'Accept': 'image/png, application/json',
        'x-api-key': photoroomtoken
    }

    files = { # el documento que contiene la imagen
        'imageFile': open(f'{relative_image_path}', 'rb')
    }

    data = { # el prompt sobre el que estará puesto el producto
        'prompt': prompt
    }

    response = requests.post(url, headers=headers, files=files, data=data) # el post request al endpoint

    date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') # encontramos la fecha actual para nombrar a la imagen correcta 
    file_path = f'functions/product_pictures/product_pictures_corrected/{date}-corrected-product-image.png' # el path de la imagen correcta dentro de un folder destinado a ello 

    if response.status_code == 200: # si el estatus de la llamada es igual a 200, entonces seguimos
        # Calcular costos de generar imagen con lightroom
        conversationCostCalculator.image_generation_costs("photoroom")
        with open(file_path, 'wb') as corrected_image: # guardamos la imagen 
            corrected_image.write(response.content)
        return file_path # regresamos el file path con el que el chatbot desplegará la imagen 
    else: # si no es 200 marcamos error 
        print("Error:", response.status_code, response.text)
        return 0

# esta es la función original para crear imágenes. El punto es que el modelo ya haya produdido una idea que le mandará aquí como referencia para crear la imagen. 
def generateInstagramImage(idea,descripcion_negocio=0,estilo=0,es_de_producto=0,feedback=0):
  
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
      product_pic_path = create_product_image(response)
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
      size="1024x1024",
      response_format = "b64_json"
    )

    # Calcular costos de gpt4
    conversationCostCalculator.image_generation_costs(model)

    # Esta funcionalidad es para guardar la imagen en vez de tenerla en un url, por el error que me encontré. En el MVP tendremos que guardar estas funciones en una función provisional en la nube. 
    image_data = base64.b64decode(image_response.data[0].b64_json)

    save_directory = 'functions/saved_images'

    # Save the image to a file in the specified directory
    file_path = os.path.join(save_directory, f'image-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.png')
    with open(file_path, 'wb') as file:
        file.write(image_data)

    return file_path  # Return the local path to the saved image
