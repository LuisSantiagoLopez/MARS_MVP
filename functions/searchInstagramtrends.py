import os  # Importa el módulo os para interactuar con el sistema operativo.
from settings.settings import apifyclient, openaiclient  # Importa clientes específicos de un módulo de configuraciones.
from datetime import datetime  # Importa datetime para manipulaciones de fechas.
from ast import literal_eval  # Importa literal_eval para evaluar de forma segura una cadena como una expresión de Python.

# Esta función entiende la publicación que el scraper encontró en el internet
def process_image_with_vision(image_url, caption_image):
    try:
        # El modelo de gpt4 with vision es capaz de entender los contenidos de una imagen
        response = openaiclient.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        # Este prompt emplea el caption de la imagen para entender mejor la imagen enviada.
                        {"type": "text", "text": f"""Describe en detalle la imagen de la publicación de Instagram enlazada. Emplea el caption de la publicación como contexto de la imagen: '{caption_image}'"""},
                        # Podemos enviar directamente el url que facebook encontró 
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                    ],
                }
            ],
            max_tokens=300, # Tenemos que reducir el número de tokens producidas, dado que podrían ser muchas imagenes. 
        )
        # devuelve el mensaje de vision, que contiene la descripción de la imagen
        return response.choices[0].message.content
    except Exception as e:
        # Devuelve un mensaje de error si ocurre una excepción.
        return f"Error al procesar la imagen: {e}"

# Define una función para buscar tendencias en Instagram basadas en una lista de palabras.
def searchInstagramTrends(palabra): 
    # Inicializa una cadena para acumular resultados.
    result_string = ""

    # Convierte la cadena de entrada (tres palabras) en una lista.
    three_word_list = literal_eval(palabra)

    # Itera sobre cada palabra en la lista.
    for word in three_word_list:
        # Prepara la entrada para el raspador de Instagram.
        run_input = {
            "directUrls": [f"https://www.instagram.com/explore/tags/{word}/"],
            "resultsType": "posts",
            "resultsLimit": 17,
            "searchType": "hashtag",
            "searchLimit": 1,
        }

        # Ejecuta el actor del raspador de Instagram con la entrada preparada.
        run = apifyclient.actor("apify/instagram-scraper").call(run_input=run_input)

        # Crea una carpeta principal para las imágenes descargadas.
        main_folder = "downloaded_images"
        os.makedirs(main_folder, exist_ok=True)
        # Genera un nombre único de carpeta basado en la fecha actual.
        run_folder = datetime.now().strftime('%Y-%m-%d')
        # Crea una ruta para la carpeta de esta ejecución.
        run_path = os.path.join(main_folder, run_folder)
        os.makedirs(run_path, exist_ok=True)

        # Itera a través de los elementos raspados.
        for item in apifyclient.dataset(run["defaultDatasetId"]).iterate_items():
            # Verifica si la publicación tiene más de 100 me gusta.
            if item['likesCount'] > 100:
                # Obtiene la URL de la imagen y el subtítulo del post.
                cover_image_url = item['displayUrl']
                caption_image = item['caption']

                # Procesa la imagen con la API de visión.
                vision_response = process_image_with_vision(cover_image_url, caption_image)
                # Si se recibe una respuesta, obtiene el contenido de la respuesta.
                if vision_response:
                    message_content = vision_response.message.content

                # Concatena la descripción procesada de la imagen a la cadena de resultados.
                result_string += f"""\n ====== \n {message_content} \n ====== \n"""

    # Devuelve la cadena concatenada de todos los resultados.
    return result_string