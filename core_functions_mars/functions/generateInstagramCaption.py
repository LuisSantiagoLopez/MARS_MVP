from ..settings.settings import openaiclient

def generateInstagramCaption(idea, conversationCostCalculator, descripcion_negocio=0,descripcion_imagen=0, feedback=0, estilo=0):
  prompt=f"""Tu tarea es generar un caption para instagram a partir de la idea dentro de las etiquetas XML. Asimismo, tienes disponible una descripción de la imagen que irá adjunta con tu caption dentro de las etiquetas XML. Dependiendo de la idea, puedes crear un caption largo o corto, pero que exprese la idea a la audiencia. Emplea el estilo de escritura especificado por el negocio en las etiquetas XML.No incluyas las etiquetas XML en tu escrito, solamente tienen la finalidad de brindarle estructura a este prompt. 
  <idea>{idea}</idea>
  {"<descripción_imagen>{descripcion_imagen}</descripción_imagen>" if descripcion_imagen !=0 else ""}
  {"<descripción_negocio>{descripcion_negocio}</descripción_negocio>" if descripcion_negocio !=0 else ""}
  {"<feedback previo del usuario>{feedback}</feedback previo del usuario>" if feedback !=0 else ""}
  {"<estilo>{estilo}</estilo>" if estilo!=0 else ""}
  """

  model = "gpt-4-1106-preview"

  response = openaiclient.chat.completions.create( # mandamos el request al api de openai
    model=model,
    messages=[
      {"role": "system", "content": "Tu trabajo es generar captions de publicaciones de instagram."},
      {"role": "user", "content": prompt},
    ]
  )

  # Calcular costos de generaciones de GPT4
  conversationCostCalculator.calculate_chat_and_vision_tokens(response,model)

  return response.choices[0].message.content