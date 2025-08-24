from agents.base_agent import BaseAgent
from openai import OpenAI
from prompts import get_code_gen_prompt

class CodeGenAgent(BaseAgent):
    """
    The agent responsible for generating the code.
    """
    def generate_code(self, plan: str, error_feedback: str = None, file: str = None, audio: str = None) -> str:
         # Create client with model configuration
        client = OpenAI(
            api_key=self.model_config["api_key"],
            base_url=self.model_config["base_url"]
        )

        system_prompt = get_code_gen_prompt(self.framework_choice, error_feedback)

        user_content = f"Generate the code for the following plan:\n\n{plan}"
        if error_feedback:
            user_content += f"\n\nThe previous attempt failed. Please fix the code. Error:\n{error_feedback}"
        if file:
            user_content += f"\nThe user also provided a file: {file.name}"
        if audio:
            user_content += f"\nThe user also provided an audio file: {audio.name}"
        try:
            response = client.chat.completions.create(
                model=self.model_config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
            ],
            max_tokens=8192
        )

            code = response.choices[0].message.content
            if code is None:
                return "# Error: No code generated from AI response"
            
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            return code.strip()
        except Exception as e:
            return f"# Error: {str(e)}"

    def run(self, plan: str, error_feedback: str = None, file: str = None, audio: str = None):
        return self.generate_code(plan, error_feedback, file, audio)
