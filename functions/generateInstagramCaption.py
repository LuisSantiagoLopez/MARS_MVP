from settings.settings import openaiclient

def generateInstagramCaption(idea,descripcion_negocio="No existe, ignora este rubro",descripcion_imagen="No hay descripción, ignora este rubro"):
  prompt=f"""Tu tarea es generar un caption para instagram a partir de la idea dentro de las etiquetas XML. Asimismo, tienes disponible una descripción de la imagen que irá adjunta con tu caption dentro de las etiquetas XML. Emplea el estilo de escritura especificado por el negocio en las etiquetas XML.No incluyas las etiquetas XML en tu escrito, solamente tienen la finalidad de brindarle estructura a este prompt. 
  <idea>{idea}</idea>
  <descripción_imagen>{descripcion_imagen}</descripción_imagen>
  <descripción_negocio>{descripcion_negocio}</descripción_negocio> 
  """

  response = openaiclient.chat.completions.create( # mandamos el request al api de openai
    model="gpt-4-1106-preview",
    messages=[
      {"role": "system", "content": "Tu trabajo es generar captions de publicaciones de instagram."},
      {"role": "user", "content": prompt},
    ]
  )

  return response.choices[0].message.content