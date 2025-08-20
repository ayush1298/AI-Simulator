import streamlit as st
from ui.main_ui import display_ui
from agents.configurator_agent import ConfiguratorAgent
from agents.planner_agent import PlannerAgent
from agents.code_gen_agent import CodeGenAgent
from utils.python_runner import run_python_code
import datetime


def main():
    st.set_page_config(page_title="AI Simulator", layout="wide")
    
    # Display the main UI and get user inputs (updated signature to match your new model system)
    query, provider, model_config, framework_choice, start_action, run_in_playground, uploaded_file, uploaded_audio = display_ui()

    # Check if model is configured
    if not model_config or not model_config.get("api_key"):
        st.stop()  # Stop execution if no model is configured

    # Reset if provider/framework changes
    if (st.session_state.get("last_provider") != provider or
        st.session_state.get("last_framework") != framework_choice):
        # update the keys_to_clear lists to include learning content
        keys_to_clear = ["config_ideas", "generation_plan", "generated_code", "playground_code", 
                    "python_output", "python_error", "chat_history", "show_playground", 
                    "show_generated_code", "code_just_generated", "code_explanation", 
                    "show_explanation", "learning_content", "show_learning"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        st.session_state.last_provider = provider
        st.session_state.last_framework = framework_choice
        st.rerun()

    # Reset when new query is different and start_action is triggered
    if start_action:
        last_query = st.session_state.get("last_query")
        if last_query != query:
            # update the keys_to_clear lists to include learning content
            keys_to_clear = ["config_ideas", "generation_plan", "generated_code", "playground_code", 
                        "python_output", "python_error", "chat_history", "show_playground", 
                        "show_generated_code", "code_just_generated", "code_explanation", 
                        "show_explanation", "learning_content", "show_learning"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.last_query = query
            st.session_state.new_generation_started = True  # Flag to indicate new generation

    # --- AI Code Generation ---
    if start_action and framework_choice in ["PyGame (AI)", "Ursina (AI)"]:
        if not query and not uploaded_file and not uploaded_audio:
            st.warning("Please provide a query, file, or audio input.")
            return

        # Store creation timestamp for new projects
        st.session_state.creation_timestamp = datetime.datetime.now().isoformat()

        # Check if this is an example being loaded with pre-generated data
        if (st.session_state.get("example_code") and 
            st.session_state.get("example_filename") and
            st.session_state.get("example_config_ideas") and
            st.session_state.get("example_generation_plan")):
            
            # For examples with complete data, use everything directly
            example_code = st.session_state.example_code
            example_config_ideas = st.session_state.example_config_ideas
            example_generation_plan = st.session_state.example_generation_plan
            
            # Clear example data
            del st.session_state.example_code
            del st.session_state.example_filename
            del st.session_state.example_config_ideas
            del st.session_state.example_generation_plan
            if "example_query" in st.session_state:
                del st.session_state.example_query
            
            # Use the pre-generated data directly (no AI calls needed)
            st.session_state.config_ideas = example_config_ideas
            st.session_state.generation_plan = example_generation_plan
            st.session_state.generated_code = example_code
            st.session_state.playground_code = example_code
            st.session_state.code_just_generated = True
            
        elif st.session_state.get("example_code") and st.session_state.get("example_filename"):
            # For examples with only code, generate config/plan based on existing code
            example_code = st.session_state.example_code
            example_filename = st.session_state.example_filename
            
            # Clear example data
            del st.session_state.example_code
            del st.session_state.example_filename
            if "example_query" in st.session_state:
                del st.session_state.example_query
            
            # Generate config ideas and plan based on existing code
            configurator = ConfiguratorAgent(model_config, framework_choice)
            planner = PlannerAgent(model_config, framework_choice)
            
            with st.spinner("🤔 Analyzing example and generating configuration ideas..."):
                config_prompt = f"""
                Analyze this existing {framework_choice.replace(' (AI)', '')} code and suggest what interactive features and configurations it demonstrates:
                
                Query: {query}
                
                Existing Code:
                {example_code}
                
                Please describe the interactive features, physics parameters, and configuration options that this code implements.
                """
                config_ideas = configurator.suggest_configurations(config_prompt, uploaded_file, uploaded_audio)
            st.session_state.config_ideas = config_ideas
            
            with st.spinner("🤖 Creating implementation plan based on example..."):
                plan_prompt = f"""
                Create a detailed plan for this {framework_choice.replace(' (AI)', '')} simulation based on the existing implementation:
                
                Query: {query}
                
                Configuration Ideas: {config_ideas}
                
                Existing Code Structure:
                {example_code}
                
                Please create a plan that describes how this simulation is structured and what it accomplishes.
                """
                plan = planner.create_plan(plan_prompt, config_ideas, uploaded_file, uploaded_audio)
            st.session_state.generation_plan = plan
            
            # Use the example code directly
            st.session_state.generated_code = example_code
            st.session_state.playground_code = example_code
            st.session_state.code_just_generated = True
            
        else:
            # Normal generation process
            # Initialize agents with model_config instead of model_choice
            configurator = ConfiguratorAgent(model_config, framework_choice)
            planner = PlannerAgent(model_config, framework_choice)
            code_generator = CodeGenAgent(model_config, framework_choice)

            # Step 1: Config ideas
            with st.spinner("🤔 Configurator Agent is brainstorming interactive features..."):
                config_ideas = configurator.suggest_configurations(query, uploaded_file, uploaded_audio)
            st.session_state.config_ideas = config_ideas

            # Step 2: Plan
            with st.spinner("🤖 Planner Agent is creating a detailed plan..."):
                plan = planner.create_plan(query, config_ideas, uploaded_file, uploaded_audio)
            st.session_state.generation_plan = plan

            # Step 3: Code generation
            with st.spinner("💻 Code Generation Agent is building the simulation..."):
                generated_code = code_generator.generate_code(plan, file=uploaded_file, audio=uploaded_audio)
            st.session_state.generated_code = generated_code
            st.session_state.playground_code = generated_code
            st.session_state.code_just_generated = True  # Flag to auto-collapse the expander
        
        # Clear the new generation flag and refresh
        if "new_generation_started" in st.session_state:
            del st.session_state.new_generation_started
        st.rerun()

    # --- Playground Execution ---
    if run_in_playground:
        code_to_run = st.session_state.get("playground_code", "")
        if not code_to_run:
            st.warning("There is no code in the playground to run.")
            return

        with st.spinner("🐍 Executing Python code..."):
            output, error = run_python_code(code_to_run)

        st.session_state.python_output = output
        st.session_state.python_error = error
        st.rerun()


if __name__ == "__main__":
    main()