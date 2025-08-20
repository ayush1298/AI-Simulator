import streamlit as st
import os
from typing import Dict, Tuple, Optional
from config.models_config import (
    MODEL_PROVIDERS, 
    COST_COLORS, 
    DEFAULT_PROVIDER, 
    DEFAULT_MODEL,
    get_provider_models,
    get_model_info,
    get_api_config
)

class ModelSelector:
    """Handles model selection UI and configuration"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state for model selection"""
        if "selected_provider" not in st.session_state:
            st.session_state.selected_provider = DEFAULT_PROVIDER
        
        if "selected_model" not in st.session_state:
            st.session_state.selected_model = DEFAULT_MODEL
        
        if "api_keys" not in st.session_state:
            st.session_state.api_keys = {}
    
    def display_model_selector(self) -> Tuple[str, str, str, Dict]:
        """
        Display the model selection interface
        Returns: (provider, model_id, api_key, model_config)
        """
        st.markdown("### 🤖 AI Model Configuration")
        
        # Provider selection
        col1, col2 = st.columns([1, 1])
        
        with col1:
            provider = st.selectbox(
                "Select AI Provider:",
                options=list(MODEL_PROVIDERS.keys()),
                index=list(MODEL_PROVIDERS.keys()).index(st.session_state.selected_provider),
                key="provider_select",
                help="Choose your preferred AI provider"
            )
        
        # Update session state if provider changed
        if provider != st.session_state.selected_provider:
            st.session_state.selected_provider = provider
            # Reset model selection when provider changes
            models = get_provider_models(provider)
            if models:
                st.session_state.selected_model = list(models.keys())[0]
            st.rerun()
        
        # Model selection
        with col2:
            models = get_provider_models(provider)
            if models:
                model_options = list(models.keys())
                
                # Ensure selected model is valid for current provider
                if st.session_state.selected_model not in model_options:
                    st.session_state.selected_model = model_options[0]
                
                model_id = st.selectbox(
                    "Select Model:",
                    options=model_options,
                    index=model_options.index(st.session_state.selected_model),
                    format_func=lambda x: models[x]["name"],
                    key="model_select",
                    help="Choose the specific model variant"
                )
                
                # Update session state
                st.session_state.selected_model = model_id
            else:
                st.error(f"No models available for {provider}")
                return None, None, None, None
        
        # Display model information
        model_info = get_model_info(provider, model_id)
        if model_info:
            with st.expander("📋 Model Information", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Name:** {model_info['name']}")
                    st.markdown(f"**Provider:** {provider}")
                
                with col2:
                    cost_color = COST_COLORS.get(model_info.get('cost', 'Medium'), '🟡')
                    st.markdown(f"**Cost:** {cost_color} {model_info.get('cost', 'Medium')}")
                    st.markdown(f"**Max Tokens:** {model_info.get('max_tokens', 'N/A')}")
                
                with col3:
                    st.markdown(f"**Description:**")
                    st.markdown(model_info.get('description', 'No description available'))
        
        # API Key input
        st.markdown("### 🔑 API Configuration")
        
        provider_config = MODEL_PROVIDERS[provider]
        api_key_env = provider_config["api_key_env"]
        
        # Get API key from environment or session state
        env_key = os.getenv(api_key_env, "")
        current_key = st.session_state.api_keys.get(provider, env_key)
        
        # API key input with helpful information
        col1, col2 = st.columns([2, 1])
        
        with col1:
            api_key = st.text_input(
                f"{provider} API Key:",
                value=current_key,
                type="password",
                key=f"api_key_{provider}",
                help=f"Enter your {provider} API key. You can get one from their official website."
            )
        
        with col2:
            st.markdown("**Get API Key:**")
            api_links = {
                "OpenAI": "https://platform.openai.com/api-keys",
                "Anthropic": "https://console.anthropic.com/",
                "Google": "https://makersuite.google.com/app/apikey",
                "DeepSeek": "https://platform.deepseek.com/api_keys",
                "Mistral": "https://console.mistral.ai/api-keys/",
                "Cerebras": "https://cloud.cerebras.ai/api-keys",
                "Grok": "https://console.grok.com/api-keys", 
                "OpenRouter": "https://openrouter.ai/keys"
            }
            
            if provider in api_links:
                st.markdown(f"[Get {provider} API Key]({api_links[provider]})")
        
        # Store API key in session state
        st.session_state.api_keys[provider] = api_key
        
        # Validation
        if not api_key:
            st.warning(f"⚠️ Please enter your {provider} API key to continue.")
            return provider, model_id, None, None
        
        # Get model configuration
        model_config = get_api_config(provider, model_id, api_key)
        
        # Success message
        st.success(f"✅ Ready to use {model_info.get('name', model_id)} from {provider}")
        
        return provider, model_id, api_key, model_config

def display_model_selector_compact() -> Tuple[str, str, str, Dict]:
    """
    Compact version of model selector for sidebar
    Returns: (provider, model_id, api_key, model_config)
    """
    selector = ModelSelector()
    
    st.subheader("🤖 AI Model")
    
    # Provider selection
    provider = st.selectbox(
        "Provider:",
        options=list(MODEL_PROVIDERS.keys()),
        index=list(MODEL_PROVIDERS.keys()).index(st.session_state.get("selected_provider", DEFAULT_PROVIDER)),
        key="sidebar_provider_select"
    )
    
    # Model selection
    models = get_provider_models(provider)
    if models:
        model_options = list(models.keys())
        current_model = st.session_state.get("selected_model", model_options[0])
        
        if current_model not in model_options:
            current_model = model_options[0]
        
        model_id = st.selectbox(
            "Model:",
            options=model_options,
            index=model_options.index(current_model),
            format_func=lambda x: models[x]["name"],
            key="sidebar_model_select"
        )
    else:
        st.error(f"No models for {provider}")
        return None, None, None, None
    
    # Model info display
    model_info = get_model_info(provider, model_id)
    if model_info:
        cost_color = COST_COLORS.get(model_info.get('cost', 'Medium'), '🟡')
        st.caption(f"{cost_color} {model_info.get('cost', 'Medium')} cost • {model_info['description'][:50]}...")
    
    # API Key
    provider_config = MODEL_PROVIDERS[provider]
    api_key_env = provider_config["api_key_env"]
    env_key = os.getenv(api_key_env, "")
    current_key = st.session_state.api_keys.get(provider, env_key)
    
    api_key = st.text_input(
        f"{provider} API Key:",
        value=current_key,
        type="password",
        key=f"sidebar_api_key_{provider}",
        placeholder="Enter API key..."
    )
    
    # Store in session state
    st.session_state.api_keys[provider] = api_key
    st.session_state.selected_provider = provider
    st.session_state.selected_model = model_id
    
    if not api_key:
        st.warning(f"⚠️ API key required")
        return provider, model_id, None, None
    
    model_config = get_api_config(provider, model_id, api_key)
    return provider, model_id, api_key, model_config