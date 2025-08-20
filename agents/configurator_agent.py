from agents.base_agent import BaseAgent
from openai import OpenAI
from prompts import get_configurator_prompt

class ConfiguratorAgent(BaseAgent):
    """
    The agent responsible for brainstorming interactive features for the simulation.
    """
    def suggest_configurations(self, query: str, file: str = None, audio: str = None) -> str:
        # Create client with model configuration
        client = OpenAI(
            api_key=self.model_config["api_key"],
            base_url=self.model_config["base_url"]
        )

        framework_name = self.framework_choice.replace(' (AI)', '')
        system_prompt = get_configurator_prompt(framework_name)

        user_content = f"Here is the user's request: {query}"
        if file:
            user_content += f"\nThe user also provided a file: {file.name}"
        if audio:
            user_content += f"\nThe user also provided an audio file: {audio.name}"

        response = client.chat.completions.create(
            model=self.model_config["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=4096
        )
        return response.choices[0].message.content

    def run(self, query: str, file: str = None, audio: str = None):
        return self.suggest_configurations(query, file, audio)