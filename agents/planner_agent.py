from agents.base_agent import BaseAgent
from openai import OpenAI
from prompts import get_planner_prompt

class PlannerAgent(BaseAgent):
    """
    The agent responsible for creating a plan to generate the code.
    """
    def create_plan(self, query: str, config_ideas: str, file: str = None, audio: str = None) -> str:
        # Create client with model configuration
        client = OpenAI(
            api_key=self.model_config["api_key"],
            base_url=self.model_config["base_url"]
        )

        system_prompt = get_planner_prompt(self.framework_choice)

        user_content = f"""
        Original user request: {query}

        Incorporate these configuration ideas to make the simulation interactive and engaging:
        {config_ideas}
        """
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

    def run(self, query: str, config_ideas: str, file: str = None, audio: str = None):
        return self.create_plan(query, config_ideas, file, audio)