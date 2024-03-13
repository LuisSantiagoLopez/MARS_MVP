from .functions.functions_assistant_list import (
    scrapeUserWebsiteFunclist, 
    searchInstagramTrendsFunclist, 
    understandUserProductFunclist, 
    generateInstagramImageFunclist, 
    generateInstagramCaptionFunclist, 
    uploadInstagramImageFunclist
)

from .functions.scrapeUserWebsite import scrapeUserWebsite
from .functions.searchInstagramTrends import searchInstagramTrends
from .functions.understandUserProduct import understandUserProduct
from .functions.generateInstagramImage import generateInstagramImage
from .functions.generateInstagramCaption import generateInstagramCaption
from .database_management_business_logic import save_database_chat_data, save_chat_session
from .settings.settings import openaiclient
from user_payments.cost_analyzer import ConversationCostCalculator
from chatbot.models import ChatSession
import logging
import os
import time
import json

logger = logging.getLogger('application')

class Assistant:
    def __init__(self, user, chat_session_id=None):
        self.assistant_instructions = self._read_instructions("instructions_assistant_2.txt")
        self.model_assistant_main = "gpt-4-1106-preview"
        self.chat_session_given = False
        self.user = user

        if chat_session_id:
            self.chat_session_given = True
            self.chat_session_id = chat_session_id
            self.chat_session = ChatSession.objects.get(user=self.user, id=self.chat_session_id)
            assistant_id = self.chat_session.assistant_id
            thread_id = self.chat_session.thread_id
            self.assistant_main_content_creation = self._get_existing_assistant(assistant_id)
            self.main_message_thread = self._get_existing_thread(thread_id)
        else:
            self.assistant_main_content_creation = self._create_assistant()
            self.main_message_thread = openaiclient.beta.threads.create()

    def _get_existing_assistant(self, assistant_id):
        # Code to retrieve the existing assistant object based on assistant_id
        return openaiclient.beta.assistants.retrieve(assistant_id=assistant_id)

    def _get_existing_thread(self, thread_id):
        # Code to retrieve the existing thread object based on thread_id
        return openaiclient.beta.threads.retrieve(thread_id=thread_id)

    def _read_instructions(self, filename):
        from django.conf import settings
        file_path = os.path.join(settings.BASE_DIR, 'core_functions_mars', filename)

        try:
            with open(file_path, "r") as instructions:
                return instructions.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Unable to find the file: {file_path}")

    def _create_assistant(self):
        return openaiclient.beta.assistants.create(
            instructions=self.assistant_instructions,
            name="Creador de contenido para Instagram",
            model=self.model_assistant_main,
            tools=[
                scrapeUserWebsiteFunclist,
                searchInstagramTrendsFunclist,
                understandUserProductFunclist,
                generateInstagramImageFunclist,
                generateInstagramCaptionFunclist,
                uploadInstagramImageFunclist
            ],
        )

    def generate_assistant_response(self, user_message, user_input_image):

        if self.chat_session_given == False:
            self.chat_session_id = save_chat_session(self.user, self.assistant_main_content_creation, self.main_message_thread)
            self.chat_session = ChatSession.objects.get(user=self.user, id=self.chat_session_id)
            
        self.chat_instance_id = save_database_chat_data(chat_session=self.chat_session, user_message=user_message, user_input_image=user_input_image)

        user_message_json = self._concat_json_user_message(user_message)

        #self._send_user_message(user_message)
        self._send_user_message(user_message_json)

        # Creamos un nuevo objeto de ConversationCostCalculator 
        self.conversationCostCalculator = ConversationCostCalculator(user=self.user)

        return self._process_run()

    def _send_user_message(self, user_message):
        openaiclient.beta.threads.messages.create(
            self.main_message_thread.id,
            role="user",
            content=user_message,
        )

    def _process_run(self):
        run = openaiclient.beta.threads.runs.create(
            thread_id=self.main_message_thread.id,
            assistant_id=self.assistant_main_content_creation.id
        )

        while True:
            time.sleep(5)
            run_status = self._get_run_status(run.id)

            if run_status.status == 'completed':
                self.conversationCostCalculator.calculate_assistant_tokens(run_status)
                return self._handle_completed_run()

            elif run_status.status == 'requires_action':
                self._handle_action_required(run.id, run_status)

            else:
                print("Waiting for the Assistant to process...")

    def _get_run_status(self, run_id):
        return openaiclient.beta.threads.runs.retrieve(
            thread_id=self.main_message_thread.id,
            run_id=run_id
        )

    def _handle_completed_run(self):
        messages = openaiclient.beta.threads.messages.list(
            thread_id = self.main_message_thread.id,
            order = "desc"
        )

        last_message = messages.data[0]
        last_message_content = last_message.content[0].text.value
        logger.debug(f"last_message_content: {last_message_content}")

        #last_message_content_json = self._add_json_output_specification(last_message_content)
        #text_response, created_image_url = save_database_chat_data(chat_instance_id = self.chat_instance_id, assistant_response = last_message_content_json)

        text_response, created_image_url = save_database_chat_data(chat_instance_id = self.chat_instance_id, assistant_response = last_message_content)

        return text_response, created_image_url

    def _handle_action_required(self, run_id, run_status):
        print("Function Calling")
        required_actions = run_status.required_action.submit_tool_outputs.model_dump()
        print(required_actions)
        tool_outputs = self._execute_tool_actions(required_actions)
        self._submit_tool_outputs(run_id, tool_outputs)

    def _execute_tool_actions(self, required_actions):
        tool_outputs = []
        for action in required_actions["tool_calls"]:
            output = self._execute_tool(action)
            tool_outputs.append({
                "tool_call_id": action['id'],
                "output": output
            })
        return tool_outputs

    def _execute_tool(self, action):
        function_name = action['function']['name']
        function_arg = json.loads(action['function']['arguments'])
        logger.debug(f"{action['function']}")

        tool_functions = {
            "scrapeUserWebsite": scrapeUserWebsite,
            "searchInstagramTrends": searchInstagramTrends,
            "understandUserProduct": understandUserProduct,
            "generateInstagramImage": generateInstagramImage,
            "generateInstagramCaption": generateInstagramCaption,
            "uploadInstagramImage": lambda args: "not ready to upload yet"
        }

        if function_name in tool_functions:
            if function_name=="generateInstagramImage" or function_name=="understandUserProduct": 
                return tool_functions[function_name](**function_arg, chat_instance_id = self.chat_instance_id, conversationCostCalculator = self.conversationCostCalculator) 
            else: 
                return tool_functions[function_name](**function_arg, conversationCostCalculator = self.conversationCostCalculator)
        else:
            raise ValueError(f"Unknown function: {function_name}")

    def _submit_tool_outputs(self, run_id, tool_outputs):
        openaiclient.beta.threads.runs.submit_tool_outputs(
            thread_id=self.main_message_thread.id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )
        print("Submitting outputs back to the Assistant...")

    def _add_json_output_specification(self, output):
        print(f"PRE-JSON: {output}")

        json_instructions = f'''
        Cuando recibas una respuesta de otro modelo de lenguaje dentro de las triple backticks, por favor Formatea la respuesta siguiendo este esquema JSON:

            {{
                "response": "Aquí va la respuesta casi idéntica a la del otro modelo de lenguaje, si acaso con alguna modificación para aumentar la coherencia de la respuesta con respecto al cambio de formato a JSON.",
                "db_id": "Si aplicable, incluye el id que indica el lugar en la base de datos donde se encuentra el path de la imagen generada por el modelo original. Si no hay ningún id, omite esta clave."
            }}

            - Clave "response": Incluye la respuesta modificada dentro de las comillas.
            - Clave "db_id": Si el modelo original generó una imagen y proporcionó un ID, inclúyelo aquí. De lo contrario, omite esta clave.

        4. Consejos Adicionales:
            - Mantén la estructura del JSON como se especifica. No alteres las claves ni añadas claves adicionales.
            - Evita incluir la palabra "json" antes de la respuesta.

        respuesta del otro modelo de lenguaje: ```{output}```
        '''

        model = "gpt-4-1106-preview"

        response = openaiclient.chat.completions.create(
            model=model,
            response_format={ "type": "json_object" },
            messages=[
            {"role": "system", "content": "Tu trabajo es formatear las respuestas de otros modelos de lenguaje a JSON."},
            {"role": "user", "content": json_instructions},
            ]
        )

        new_response = response.choices[0].message.content

        self.conversationCostCalculator.calculate_chat_and_vision_tokens(response, model)

        return new_response
    
    def _concat_json_user_message(self, user_message): 
        json_string = """. ###Responde en JSON### Estructura tu respuesta con el siguiente formato JSON:

            {{
                "response": "Aquí va la respuesta casi idéntica a la del otro modelo de lenguaje, si acaso con alguna modificación para aumentar la coherencia de la respuesta con respecto al cambio de formato a JSON.",
                "db_id": "Si aplicable, incluye el id que indica el lugar en la base de datos donde se encuentra el path de la imagen generada por el modelo original. Si no hay ningún id, omite esta clave."
            }}

            - Clave "response": Incluye la respuesta modificada dentro de las comillas.
            - Clave "db_id": Si el modelo original generó una imagen y proporcionó un ID, inclúyelo aquí. De lo contrario, omite esta clave.

        Requisitos: 
            - Mantén la estructura del JSON como se especifica. No alteres las claves ni añadas claves adicionales. Serás penalizado si tu respuesta no es puramente JSON que pueda traducirse a un diccionario en código de python. 
            - Evita incluir la palabra "json" antes de la respuesta.
        """

        user_message_json = user_message + json_string

        return user_message_json

