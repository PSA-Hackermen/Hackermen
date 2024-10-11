import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage


KEY_OPENAI_API = 'openai_api_key'
load_dotenv()

def _set_api_key():
    api_key = os.getenv('OPENAI_API_KEY')
    os.environ[KEY_OPENAI_API] = api_key

class OpenAIClient:
    def __init__(self, temperature: float = 0.3, model: str = "gpt-3.5-turbo") -> None:
        _set_api_key()
        self.llm = ChatOpenAI(model=model, temperature=temperature, )

    def generate(self, user_prompt: str,
             system_context: str = """You are an advanced AI model that serves to provide edge weights for a 
             graph whose nodes represent ports. We will give you weather condition logs for the past three days
             and your job is to give us appropriate weights for each provided location provided based on the difficulty of travel.
             Please answer using the json format {"[a tuple latitude and longitude that is given to you in the HumanMessage]" : "[respective difficulty of sailing in the area on a scale of 0.0 to 10.0]}"""):

        system_message = AIMessage(content=system_context)
        human_message = HumanMessage(content=user_prompt)  # Directly use user_prompt here
        messages = [system_message, human_message]
        res = self.llm.invoke(messages).content.strip()
        return res
