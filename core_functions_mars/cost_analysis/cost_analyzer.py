import tiktoken
from ..settings.settings import openaiclient
import os
import pandas as pd

csv_file = "core_functions_mars/cost_analysis/cost_record.csv"

if os.path.exists(csv_file):
    cost_record = pd.read_csv(csv_file)
else:
    cost_record = pd.DataFrame(columns=['User', 'Model', 'Cost', 'Timestamp', 'Real Cost', 'Use Case', 'Context Tokens', 'Output Tokens'])

class ConversationCostCalculator:
    def __init__(self, user):
        self.accumulated_cost = 0
        self.user = user 

    def calculate_cost(self, num_tokens_input=0, num_tokens_output=0, cost_rate_input=0.01, cost_rate_output=0.03, cost_rate_vision_image=0, photoroom_cost=0, dalle3_cost=0, apify_run_cost_usd = 0, model="", use_case=""):

        if model == "gpt-3.5-turbo-1106":
            cost_rate_input = 0.001
            cost_rate_output = 0.002

        total_cost = (num_tokens_input / 1000 * cost_rate_input) + (num_tokens_output / 1000 * cost_rate_output)
        total_cost += cost_rate_vision_image + photoroom_cost + dalle3_cost + apify_run_cost_usd

        global cost_record
        cost_entry = pd.DataFrame({'User': [self.user],'Model': [model], 'Cost': [total_cost], 'Timestamp': [pd.Timestamp.now()], 'Real Cost': [None], 'Use Case': [use_case], 'Context Tokens': [num_tokens_input], 'Output Tokens': [num_tokens_output]})

        cost_record = pd.concat([cost_record, cost_entry], ignore_index=True)

        cost_record.to_csv(csv_file, index=False)

        self.accumulated_cost += total_cost
        return total_cost
    
        """
    def calculate_assistant_tokens(self, assistant, thread):
        model = assistant.model
        messages = openaiclient.beta.threads.messages.list(thread_id=thread.id)
        
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        
        tokens_per_message = 4
        num_tokens_input = 0
        num_tokens_output = 0
        

        for msg in messages.data:
            content_value = msg.content[0].text.value
            num_tokens_input += tokens_per_message
            if msg.role == "user":
                num_tokens_input += len(encoding.encode(content_value))
                print("accounted for user message")
            if msg.role == "assistant":
                print("accounted for assistant's message")
                num_tokens_output += len(encoding.encode(content_value))
                num_tokens_output += 3

        tokens_instructions = len(encoding.encode(assistant.instructions))
        num_tokens_input += tokens_instructions

        self.calculate_cost(num_tokens_input, num_tokens_output, model=model, use_case="assistant")
        """

    def calculate_assistant_tokens(self, run):
        usage_info = run.usage

        num_tokens_input = usage_info['prompt_tokens']
        num_tokens_output = usage_info['completion_tokens']

        self.calculate_cost(num_tokens_input, num_tokens_output, model="gpt-4-1106-preview", use_case="assistant")

        """
    def calculate_function_io_tokens(self, func_inputs=0, func_outputs=0, assistant=0):
        model = assistant.model

        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        num_tokens_output = 0
        num_tokens_output += len(encoding.encode(func_outputs))
        num_tokens_output += len(encoding.encode(func_inputs))
    
        self.calculate_cost(num_tokens_output=num_tokens_output, model=model, use_case="function")
        """

    def calculate_chat_and_vision_tokens(self, completion, model):
        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens

        if input_tokens and output_tokens: 
            print("CORRECTLY REGISTERED CHATGPT COMPLETION")

        cost_rate_vision_image = 0
        if model == "gpt-4-vision-preview": 
            use_case="vision" 
            cost_rate_vision_image = 0.00765
        else:
            use_case="json or other function"

        self.calculate_cost(num_tokens_input=input_tokens, num_tokens_output=output_tokens, cost_rate_vision_image=cost_rate_vision_image,model=model, use_case=use_case)

    def image_generation_costs(self, model):
        photoroom_cost = dalle3_cost = 0
        if model == "photoroom":
            photoroom_cost = 0.15
        elif model == "dall-e-3": 
            dalle3_cost = 0.04
        self.calculate_cost(photoroom_cost=photoroom_cost, dalle3_cost=dalle3_cost,model=model, use_case="photo product")

    def apify_run_costs(self, run, type):
        apify_run_cost_usd = run['usageTotalUsd']
        model = "apify website scraper" if type == "website" else "apify instagram scraper"
        self.calculate_cost(apify_run_cost_usd=apify_run_cost_usd, model=model, use_case=model)