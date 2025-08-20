from agents.base_agent import BaseAgent
from openai import OpenAI
from prompts import get_learning_prompt

class LearningAgent(BaseAgent):
    """
    The agent responsible for generating educational content related to the simulation.
    """
    def generate_learning_content(self, code: str, query: str, config_ideas: str = None, generation_plan: str = None) -> str:
        # Create client with model configuration
        client = OpenAI(
            api_key=self.model_config["api_key"],
            base_url=self.model_config["base_url"]
        )

        framework_name = self.framework_choice.replace(' (AI)', '')
        system_prompt = get_learning_prompt(framework_name)

        user_content = f"""
        Original Query: {query}
        
        Code to analyze:
        ```python
        {code}
        ```
        """
        
        if config_ideas:
            user_content += f"\n\nConfiguration Ideas:\n{config_ideas}"
        
        if generation_plan:
            user_content += f"\n\nGeneration Plan:\n{generation_plan}"

        response = client.chat.completions.create(
            model=self.model_config["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=6144  # Increased for comprehensive learning content
        )
        return response.choices[0].message.content

    def run(self, code: str, query: str, config_ideas: str = None, generation_plan: str = None):
        return self.generate_learning_content(code, query, config_ideas, generation_plan)