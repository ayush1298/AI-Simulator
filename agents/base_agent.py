from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Base class for all AI agents
    """
    def __init__(self, model_config: dict, framework_choice: str):
        """
        Initialize the agent with model configuration
        
        Args:
            model_config: Dictionary containing API config (api_key, base_url, model)
            framework_choice: The chosen framework (e.g., "PyGame (AI)")
        """
        self.model_config = model_config
        self.framework_choice = framework_choice
    
    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Abstract method that each agent must implement
        """
        pass