from functions.functions_assistant_list import (scrapeUserWebsiteFunclist, 
                                  searchInstagramTrendsFunclist, 
                                  understandUserProductFunclist, 
                                  generateInstagramImageFunclist, 
                                  generateInstagramCaptionFunclist, 
                                  uploadInstagramImageFunclist) # importando las funciones de functions assistant para modularizar correctamente el programa
from functions.scrapeUserWebsite import scrapeUserWebsite
from functions.searchInstagramTrends import searchInstagramTrends
from functions.understandUserProduct import understandUserProduct
from functions.generateInstagramImage import generateInstagramImage
from functions.generateInstagramCaption import generateInstagramCaption
from settings.settings import openaiclient
import time
import json

# En el MVP tendremos que crear un asistente general con distintos threads para cada conversación. Es importante que esto esté guardado en la base de datos. 

with open("instructions_assistant.txt", "r") as instructions: 
  assistant_instructions = instructions.read() # las instruccciones del asistente están en un documento .txt aparte 

model_assistant_main = "gpt-4-1106-preview" # el modelo que usará el asistente, que es gpt 4 para incrementar coherencia al llamar las funciones 

assistant_main_content_creation = openaiclient.beta.assistants.create(
  instructions = assistant_instructions,
  name="Creador de contenido para Instagram",
  model=model_assistant_main,
  tools=[
    scrapeUserWebsiteFunclist, # el usuario da su página web y el asistente la escanea 
    searchInstagramTrendsFunclist, # busca tendencias de su nicho en instagram 
    understandUserProductFunclist, # entiende el producto del cliente con visión 
    generateInstagramImageFunclist, # crea una foto para la audiencia o de producto 
    generateInstagramCaptionFunclist, # crea una caption para la publicación que crea 
    uploadInstagramImageFunclist # sube la publicación al instagram del usuario 
  ],
)

main_message_thread = openaiclient.beta.threads.create() # creamos el thread de mensajes 

while True:
    user_message = input("User: ") # prompt del usuario. (esto no va a ser así cuando haga la integración con django)

    if user_message == "Exit":
      break 

    thread_message = openaiclient.beta.threads.messages.create(
    main_message_thread.id,
    role="user",
    content=user_message,
    ) # añadimos el mensaje del usuario al thread, o lista de mensajes, antes de correr el chatbot 

    run = openaiclient.beta.threads.runs.create(
    thread_id=main_message_thread.id,
    assistant_id=assistant_main_content_creation.id
    ) # corremos el asistente con el id del thread y del asistente 
    
    while True:
        # Wait for 5 seconds
        time.sleep(5)

        # Retrieve the run status
        run_status = openaiclient.beta.threads.runs.retrieve(
        thread_id = main_message_thread.id,
        run_id = run.id,
        ) # volvemos a correr el asistente 

        # If run is completed, get messages
        if run_status.status == 'completed':
            messages = openaiclient.beta.threads.messages.list(
                thread_id=main_message_thread.id
            )

            # Loop through messages and print content based on role
            for msg in reversed(messages.data):
                role = msg.role
                content = msg.content[0].text.value
                print(f"{role.capitalize()}: {content}")

            break
        elif run_status.status == 'requires_action':
            print("Function Calling")
            required_actions = run_status.required_action.submit_tool_outputs.model_dump()
            print(required_actions)
            tool_outputs = []
            import json
            for action in required_actions["tool_calls"]:
                
                function_name = action['function']['name']
                function_arg = json.loads(action['function']['arguments'])
                
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
                    #output = uploadInstagramImage(**function_arg)
                    output = "not ready to upload yet"
                else:
                    raise ValueError(f"Unknown function: {function_name}")
                
                tool_outputs.append({
                        "tool_call_id": action['id'],
                        "output": output
                })
                
            print("Submitting outputs back to the Assistant...")
            openaiclient.beta.threads.runs.submit_tool_outputs(
                thread_id=main_message_thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
        else:
            print("Waiting for the Assistant to process...")
            time.sleep(5)