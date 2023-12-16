from functions.functions_assistant_list import (scrapeUserWebsite, 
                                 searchInstagramTrends, 
                                 understandUserProduct, 
                                 generateInstagramImage, 
                                 generateInstagramCaption, 
                                 uploadInstagramImage) # importando las funciones de functions assistant para modularizar correctamente el programa
from openai import OpenAI
import time

client = OpenAI() # creando un cliente de openai con el que crearé el asistente 

with open("instructions_assistant.txt", "r") as instructions: 
  assistant_instructions = instructions.read() # las instruccciones del asistente están en un documento .txt aparte 

model_assistant_main = "gpt-4-1106-preview" # el modelo que usará el asistente, que es gpt 4 para incrementar coherencia al llamar las funciones 

assistant_main_content_creation = client.beta.assistants.create(
  instructions = assistant_instructions,
  name="Creador de contenido para Instagram",
  model=model_assistant_main,
  tools=[
    scrapeUserWebsite, # el usuario da su página web y el asistente la escanea 
    searchInstagramTrends, # busca tendencias de su nicho en instagram 
    understandUserProduct, # entiende el producto del cliente con visión 
    generateInstagramImage, # crea una foto para la audiencia o de producto 
    generateInstagramCaption, # crea una caption para la publicación que crea 
    uploadInstagramImage # sube la publicación al instagram del usuario 
  ],
)

main_message_thread = client.beta.threads.create() # creamos el thread de mensajes 

exit = False # variable para salir de la conversación 

while exit==False: # empieza loop para continuar los mensajes 
  user_message = input("User: ") # prompt del usuario. (esto no va a ser así cuando haga la integración con django)

  if user_message == "Exit":
    exit = True # si el prompt del usuario es exit entonces salimos del loop
    break # si este break existe no necesitamos el exit previo, pero lo escribo así para aumentar la claridad

  thread_message = client.beta.threads.messages.create(
  main_message_thread.id,
  role="user",
  content=user_message,
  ) # añadimos el mensaje del usuario al thread, o lista de mensajes, antes de correr el chatbot 

  run = client.beta.threads.runs.create(
  thread_id=main_message_thread.id,
  assistant_id=assistant_main_content_creation.id
  ) # corremos el asistente con el id del thread y del asistente 

  i = 0

  while run.status not in ["completed", "failed", "requires_action"]: # tenemos este verificador de estatus, que ve si el run ya se completó 
    if i > 0: # si el loop corre más de una vez entonces se espera 10 segundos 
      time.sleep(10)

    run = client.beta.threads.runs.retrieve(
    thread_id = main_message_thread.id,
    run_id = run.id,
    ) # volvemos a correr el asistente 

    i += 1 # sumamos a la variable de conteo 

  if run.status == "requires_action":
    tools_to_call = run.required_action.submit_tool_outputs.tool_calls # lista de todas las funciones que el asistente llamó a partir del mensaje del usuario 

    tool_output_array = []

    for each_tool in tools_to_call: # comienza el for loop para llamar cada función
        tool_call_id = each_tool.id # extraemos el id de la función definida por openai
        function_name = each_tool.function.name # nombre de la función
        function_arg = each_tool.function.arguments # guardamos los argumentos de la función 

        # imprimimos los detalles de la function call
        print("Tool ID: " + tool_call_id)
        print("Function to call: " + function_name)
        print("Parameters to use: " + function_arg)

        # Llamamos una función dependiendo de 
        if function_name == "scrapeUserWebsite":
            output = scrapeUserWebsite(**function_arg)
        elif function_name == "searchInstagramTrends":
            output = searchInstagramTrends(**function_arg)
        elif function_name == "understandUserProduct":
            output = understandUserProduct(**function_arg)
        elif function_name == "generateInstagramImage":
            output = generateInstagramImage(**function_arg)
        elif function_name == "generateInstagramCaption":
            output = generateInstagramCaption(**function_arg)
        elif function_name == "uploadInstagramImage":
            output = uploadInstagramImage(**function_arg)

        tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

  messages = client.beta.threads.messages.list(
  thread_id = main_message_thread.id
  ) # generamos una lista de mensajes 

  for message in reversed(messages.data):
    print(message.role + ": " + message.content[0].text.value) # enseñamos cada mensaje al usuario
