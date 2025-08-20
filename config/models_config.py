"""
Model configuration for AI Simulator
"""

MODEL_PROVIDERS = {
    "OpenAI": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "models": {
            "gpt-5": {
                "name": "GPT-5",
                "description": "The latest and most capable flagship model from OpenAI.",
                "max_tokens": 8192,
                "cost": "Very High"
            },
            "gpt-4o": {
                "name": "GPT-4o",
                "description": "The latest omni-model, balances intelligence and speed.",
                "max_tokens": 4096,
                "cost": "High"
            },
            "gpt-4o-mini": {
                "name": "GPT-4o Mini",
                "description": "Fast and efficient, good for most tasks",
                "max_tokens": 4096,
                "cost": "Medium"
            },
        }
    },
    "Anthropic": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": "https://api.anthropic.com",
        "models": {
            "claude-opus-4.1": {
                "name": "Claude Opus 4.1",
                "description": "Most powerful Anthropic model for complex agentic tasks and coding.",
                "max_tokens": 4096,
                "cost": "Very High"
            },
            "claude-sonnet-4": {
                "name": "Claude Sonnet 4",
                "description": "Balanced model for enterprise use, good for coding and general tasks.",
                "max_tokens": 4096,
                "cost": "High"
            },
            "claude-3-5-sonnet-20241022": {
                "name": "Claude 3.5 Sonnet",
                "description": "Most capable Claude model for complex tasks",
                "max_tokens": 4096,
                "cost": "High"
            },
            "claude-3-5-haiku-20241022": {
                "name": "Claude 3.5 Haiku",
                "description": "Fast and efficient Claude model",
                "max_tokens": 4096,
                "cost": "Medium"
            },
            "claude-3-opus-20240229": {
                "name": "Claude 3 Opus",
                "description": "Previous generation flagship model",
                "max_tokens": 4096,
                "cost": "High"
            }
        }
    },
    "Google": {
        "api_key_env": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models": {
            "gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "description": "Google's most capable and advanced reasoning model.",
                "max_tokens": 8192,
                "cost": "Very High"
            },
            "gemini-2.0-flash": {
                "name": "Gemini 2.0 Flash",
                "description": "Latest Gemini model, fast and capable",
                "max_tokens": 4096,
                "cost": "Medium"
            },
            "gemini-1.5-pro": {
                "name": "Gemini 1.5 Pro",
                "description": "Advanced reasoning and large context",
                "max_tokens": 4096,
                "cost": "High"
            },
            "gemini-1.5-flash": {
                "name": "Gemini 1.5 Flash",
                "description": "Fast and efficient for most tasks",
                "max_tokens": 4096,
                "cost": "Medium"
            }
        }
    },
    "DeepSeek": {
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "models": {
            "deepseek-r1-0528": {
                "name": "DeepSeek R1 (0528)",
                "description": "A powerful reasoning model, excellent for complex logic.",
                "max_tokens": 8192,
                "cost": "High"
            },
            "deepseek-v3-chat": {
                "name": "DeepSeek V3 Chat",
                "description": "Latest general-purpose chat model from DeepSeek.",
                "max_tokens": 8192,
                "cost": "Medium"
            },
            "deepseek-coder-v2": {
                "name": "DeepSeek Coder V2",
                "description": "A highly capable, specialized model for coding tasks.",
                "max_tokens": 8192,
                "cost": "Medium"
            }
        }
    },
    "Mistral": {
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
        "models": {
            "mistral-large-2": {
                "name": "Mistral Large 2",
                "description": "The latest flagship model from Mistral, with top-tier reasoning.",
                "max_tokens": 8192,
                "cost": "Very High"
            },
            "mistral-medium-3.1": {
                "name": "Mistral Medium 3.1",
                "description": "A balanced and powerful model with multimodal capabilities.",
                "max_tokens": 8192,
                "cost": "High"
            },
            "codestral-2508": {
                "name": "Codestral (2508)",
                "description": "A new, specialized model for code generation and interaction.",
                "max_tokens": 8192,
                "cost": "Medium"
            },
            "mistral-large-latest": {
                "name": "Mistral Large",
                "description": "Most capable Mistral model",
                "max_tokens": 4096,
                "cost": "High"
            },
            "mistral-medium-latest": {
                "name": "Mistral Medium",
                "description": "Balanced performance and cost",
                "max_tokens": 4096,
                "cost": "Medium"
            },
            "mistral-small-latest": {
                "name": "Mistral Small",
                "description": "Fast and cost-effective",
                "max_tokens": 4096,
                "cost": "Low"
            }
        }
    },
    "Cerebras": {
        "api_key_env": "CEREBRAS_API_KEY",
        "base_url": "https://api.cerebras.ai/v1",
        "models": {
            "gpt-oss-120b": {
                "name": "GPT OSS 120B",
                "description": "Cerebras's largest open-source model with 120B parameters.",
                "max_tokens": 8192,
                "cost": "Medium"
            },
            "llama-4-maverick": {
                "name": "Llama 4 Maverick",
                "description": "Advanced Llama 4 variant optimized for complex reasoning.",
                "max_tokens": 8192,
                "cost": "High"
            },
            "llama-4-scout": {
                "name": "Llama 4 Scout",
                "description": "Fast and efficient Llama 4 variant for general tasks.",
                "max_tokens": 8192,
                "cost": "Medium"
            }
        }
    },
    "Grok": {
        "api_key_env": "GROK_API_KEY",
        "base_url": "https://api.grok.com/v1",
        "models": {
            "deepseek-r1-distill-llama-70b": {
                "name": "DeepSeek R1 Distill Llama 70B",
                "description": "Distilled version of DeepSeek R1 based on Llama 70B architecture.",
                "max_tokens": 8192,
                "cost": "High"
            },
            "moonshotai/kimi-k2-instruct": {
                "name": "Kimi K2 Instruct",
                "description": "MoonshotAI's instruction-tuned model for conversational AI.",
                "max_tokens": 8192,
                "cost": "Medium"
            }
        }
    },
    "OpenRouter": {
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "models": {
            "openai/gpt-5": {
                "name": "GPT-5 (OpenRouter)",
                "description": "Access OpenAI's latest model via OpenRouter.",
                "max_tokens": 8192,
                "cost": "Very High"
            },
            "anthropic/claude-opus-4.1": {
                "name": "Claude Opus 4.1 (OpenRouter)",
                "description": "Access Anthropic's flagship model via OpenRouter.",
                "max_tokens": 4096,
                "cost": "Very High"
            },
            "google/gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro (OpenRouter)",
                "description": "Access Google's top model via OpenRouter.",
                "max_tokens": 8192,
                "cost": "Very High"
            },
            "meta-llama/llama-3.1-405b-instruct": {
                "name": "Llama 3.1 405B Instruct",
                "description": "Meta's largest and most capable instruction-tuned model.",
                "max_tokens": 8192,
                "cost": "High"
            },
            "deepseek/deepseek-coder": {
                "name": "DeepSeek Coder (OpenRouter)",
                "description": "DeepSeek's coding model via OpenRouter",
                "max_tokens": 4096,
                "cost": "Low"
            },
            "anthropic/claude-3.5-sonnet": {
                "name": "Claude 3.5 Sonnet (OpenRouter)",
                "description": "Claude via OpenRouter",
                "max_tokens": 4096,
                "cost": "Medium"
            },
            "google/gemini-2.0-flash": {
                "name": "Gemini 2.0 Flash (OpenRouter)",
                "description": "Gemini via OpenRouter",
                "max_tokens": 4096,
                "cost": "Medium"
            },
            "meta-llama/llama-3.2-90b-vision-instruct": {
                "name": "Llama 3.2 90B Vision",
                "description": "Meta's vision-capable model",
                "max_tokens": 4096,
                "cost": "Medium"
            },
            "meta-llama/llama-3.2-90b-vision-instruct": {
                "name": "Llama 3.2 90B Vision",
                "description": "Meta's vision-capable model",
                "max_tokens": 4096,
                "cost": "Medium"
            },
            "qwen/qwen3-coder": {
                "name": "Qwen 3 Coder",
                "description": "Alibaba's latest coding-specialized model with advanced reasoning.",
                "max_tokens": 8192,
                "cost": "Medium"
            },
            "qwen/qwen3-235b-a22b-thinking-2507": {
                "name": "Qwen 3 235B Thinking",
                "description": "Qwen's largest thinking model with 235B parameters for complex reasoning.",
                "max_tokens": 8192,
                "cost": "Very High"
            },
            "qwen/qwen3-235b-a22b-2507": {
                "name": "Qwen 3 235B",
                "description": "Qwen's flagship 235B parameter model for general tasks.",
                "max_tokens": 8192,
                "cost": "Very High"
            }
        }
    }
}

# Cost colors for UI
COST_COLORS = {
    "Low": "🟢",
    "Medium": "🟡",
    "High": "🔴"
}

# Default selections
DEFAULT_PROVIDER = "Google"
DEFAULT_MODEL = "gemini-2.0-flash"

def get_provider_models(provider: str):
    """Get models for a specific provider"""
    return MODEL_PROVIDERS.get(provider, {}).get("models", {})

def get_model_info(provider: str, model_id: str):
    """Get detailed information about a specific model"""
    models = get_provider_models(provider)
    return models.get(model_id, {})

def get_api_config(provider: str, model_id: str, api_key: str):
    """Get API configuration for a provider/model combination"""
    provider_config = MODEL_PROVIDERS.get(provider, {})
    
    return {
        "api_key": api_key,
        "base_url": provider_config.get("base_url"),
        "model": model_id
    }