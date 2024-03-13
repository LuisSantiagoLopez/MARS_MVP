# PASO 1: ARREGLAR IMPORTS 
# PASO 2: CONEXIÓN A MODELOS 
# PASO 3: AUTOMATIZACIONES 
# PASO 4: DISPLAY GRÁFICO

from user_payments.models import CostPerUser


class ConversationCostCalculator:
    def __init__(self, user):
        self.user = user 

    def calculate_cost(self, num_tokens_input=0, num_tokens_output=0, cost_rate_input=0.01, cost_rate_output=0.03, cost_rate_vision_image=0, photoroom_cost=0, dalle3_cost=0, apify_run_cost_usd = 0, model="", use_case=""):

        if model == "gpt-3.5-turbo-1106":
            cost_rate_input = 0.001
            cost_rate_output = 0.002

        cost_instance = 0
        cost_instance = (num_tokens_input / 1000 * cost_rate_input) + (num_tokens_output / 1000 * cost_rate_output)
        cost_instance += cost_rate_vision_image + photoroom_cost + dalle3_cost + apify_run_cost_usd

        cost_instance_pesos = cost_instance * 16.67

        previous_cost_user = CostPerUser.objects.filter(user=self.user).latest('timestamp')

        previous_available_cost = float(previous_cost_user.available_cost)
        previous_accumulated_cost = float(previous_cost_user.accumulated_cost)

        available_cost = previous_available_cost - cost_instance_pesos
        accumulated_cost = previous_accumulated_cost + cost_instance_pesos

        CostPerUser.objects.create(
        user=self.user,
        accumulated_cost=accumulated_cost, 
        available_cost=available_cost, 
        cost_instance=cost_instance_pesos,
        model=model,
        use_case=use_case,
        context_tokens=num_tokens_input,
        output_tokens=num_tokens_output
        )

    def calculate_assistant_tokens(self, run):
        usage_info = run.usage

        num_tokens_input = usage_info.prompt_tokens
        num_tokens_output = usage_info.completion_tokens

        self.calculate_cost(num_tokens_input, num_tokens_output, model="gpt-4-1106-preview", use_case="assistant")

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