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
        self.llm = ChatOpenAI(model=model, temperature=temperature )

    def generate(self, user_prompt: str,
             system_context: str = """You are an advanced maritime AI model that serves to compute the most sustainable route 
             from source port to destination port within the specified travel duration in the input. You will assume that all 
             ships have technologies to get renewable energy (e.g. kinetic energy from tidal waves, solar energy, etc).
             
             We will give you a json input that contains the following:

             1. Source Port as a tuple of (latitude, longitude)
             2. Destination Port as a tuple of (latitude, longitude)
             3. Average sailing speed of the ship 
             4. The maximum travel duration allowed
             3. Nested json structure containing the coordinates of maritime landmarks and their respective weather conditions

             Using the above sea coordinates and well known paths from source port to destination port, you will output the route such that it maximises the generation of renewable energy from the ship.
             You do not need to go through every single maritime coordinate, but you can use the weather conditions to determine the best route to take.

             Please embed using the json format {"route" : [a list of intermediary maritime coordinates from src to dest]}"""):

        system_message = AIMessage(content=system_context)
        human_message = HumanMessage(content=user_prompt)  # Directly use user_prompt here
        messages = [system_message, human_message]
        res = self.llm.invoke(messages).content.strip()
        return res
