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
            system_context: str = """You are an advanced maritime AI responsible for computing the most sustainable shipping route from a source port to a destination port, given specific travel parameters. Assume that all ships are equipped with technologies that allow them to harness renewable energy sources (e.g., tidal energy, solar energy, wind power).

            Input:
            1. Source Port (name and coordinates)
            2. Destination Port (name and coordinates)
            3. Average sailing speed of the ship (in knots)
            4. Maximum travel duration allowed (in hours)
            5. A nested JSON structure that provides the coordinates of maritime landmarks and their respective weather conditions (e.g., wind speed, wave height, solar irradiance).

            Your goal:
            - Calculate the most sustainable route between the source and destination ports by maximizing the proportion of energy coming from renewable sources.
            - Minimize the route length and stay within the maximum allowed travel duration.
            - Factor in the weather conditions at maritime landmarks to optimize renewable energy use.
            - If a route cannot be found that meets the constraints, return an error message in the response.

            Output format:
            - Return the route as a JSON object, using the format: {"route": [list of intermediary maritime coordinates from source to destination]}

            Note: The route should follow known maritime paths or sea routes
            """):

        system_message = AIMessage(content=system_context)
        human_message = HumanMessage(content=user_prompt)  # Directly use user_prompt here
        messages = [system_message, human_message]
        res = self.llm.invoke(messages).content.strip()
        return res
