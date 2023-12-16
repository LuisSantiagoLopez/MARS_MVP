# este módulo ayuda a mantener el manejo de los clientes en el mismo lugar. así no tenemos que comenzar un nuevo cliente en cada módulo. 

import os 
from dotenv import load_dotenv
from openai import OpenAI
from apify_client import ApifyClient

load_dotenv()

openaitoken = os.getenv("OPENAI_API_KEY")
apifytoken = os.getenv("APIFY_TOKEN")
photoroomtoken = os.getenv('PHOTOROOM_API_KEY')

openaiclient = OpenAI(openaitoken)
apifyclient = ApifyClient(apifytoken)