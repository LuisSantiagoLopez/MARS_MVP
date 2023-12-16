from settings.settings import openaiclient, photoroomtoken
import requests
from datetime import datetime 

# esta función es la que produce una imagen de producto aceptable a partir de una mala imagen de producto.  
def create_product_image(prompt,relative_image_path): 

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

    date = datetime.now().strftime('%Y-%m-%d') # encontramos la fecha actual para nombrar a la imagen correcta 
    file_path = f'product_pictures/product_pictures_corrected/{date}-corrected-product-image.png' # el path de la imagen correcta dentro de un folder destinado a ello 

    if response.status_code == 200: # si el estatus de la llamada es igual a 200, entonces seguimos
        with open(file_path, 'wb') as corrected_image: # guardamos la imagen 
            corrected_image.write(response.content)
        return file_path # regresamos el file path con el que el chatbot desplegará la imagen 
    else: # si no es 200 marcamos error 
        print("Error:", response.status_code, response.text)
        return 0

# esta es la función original para crear imágenes. El punto es que el modelo ya haya produdido una idea que le mandará aquí como referencia para crear la imagen. 
def generateInstagramImage(descripcion_de_negocio,idea,es_de_producto):
  if es_de_producto == True: # si la publicación es de producto, entonces empleamos photoroom para crear la nueva imagen. 
    prompt = f"""Your task is to generate a prompt for a specific type of diffusion model that replaces background images for products. The image your prompt will produce will be used as an instagram post for the idea inside XML tags. Your prompt must summerise the elements of the idea into a simple stable-diffusion style prompt such as the following: "a bag on a magnificent display stand+, with many exquisite decorations+ around it-, creating an elegant and sophisticated atmosphere", if, for instance, the product advertised were a bag and the idea were to place the bag in a stand. Generate a unique prompt for each product and idea. Your prompt must be 15 words maximum. Do not include the XML tags in your response. 
    <idea>{idea}<idea/>
    """

    response = openaiclient.chat.completions.create( # mandamos el request al api de openai
    model="gpt-4-1106-preview",
    messages=[
      {"role": "system", "content": "Your job is to create prompts for diffusion models that create product images."},
      {"role": "user", "content": prompt},
    ]
  )
    
    response = response.choices[0].message.content

    if response:
      product_pic_path = create_product_image(response)
      return product_pic_path # devolvemos el path al corrected pic 

  else: # si no es de producto 
    prompt = f"""Tu tarea es generar una imagen con base a la idea dentro de las etiquetas XML. La imagen debe representar la idea para una publicación de instagram. Recuerda que los modelos de imagen a texto todavía no pueden generar texto de modo preciso, así que evita el texto en tu imagen. También considera la descripción y el estilo del instagram del negocio dentro de las etiquetas XML.
    <estilo>{descripcion_de_negocio}<estilo/>
    <idea>{idea}<idea/>
    """

    image = openaiclient.images.generate( # dejamos que dalle produzca el prompt y la imagen 
      model="dall-e-3",
      prompt=f"{prompt}",
      n=1,
      size="1024x1024"
    )

    return image.data[0].url