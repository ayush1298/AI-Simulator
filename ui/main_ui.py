import streamlit as st
from streamlit_ace import st_ace
from st_copy import copy_button
from config.api_config import OPENROUTER_API_KEY, GEMINI_API_KEY
from utils.transcription import transcribe_audio
from ui.examples_library import display_examples_section, add_to_examples_gallery
from ui.model_selector import display_model_selector_compact
import tempfile
import json
import zipfile
import io
import os
import subprocess
import sys
import re
import datetime


def explain_code(code, model_config, framework_choice):
    """Generate explanation for the given code using selected model"""
    from openai import OpenAI
    
    # Create client based on model configuration
    client = OpenAI(
        api_key=model_config["api_key"],
        base_url=model_config["base_url"]
    )
    
    framework_name = framework_choice.replace(' (AI)', '')
    
    system_prompt = f"""You are an expert code educator specializing in {framework_name}. Your task is to provide a clear, educational explanation of the given code.

    Break down the explanation into:
    1. **Overview**: What the code does overall
    2. **Key Components**: Main classes, functions, and their purposes
    3. **Interactive Features**: What users can control and how
    4. **Code Structure**: How the code is organized
    5. **Learning Points**: Educational aspects and concepts demonstrated
    
    Make the explanation accessible to both beginners and intermediate programmers."""
    
    user_content = f"Please explain this {framework_name} code:\n\n```python\n{code}\n```"
    
    response = client.chat.completions.create(
        model=model_config["model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        max_tokens=4096
    )
    
    return response.choices[0].message.content

def get_chat_context(chat_history: list, max_exchanges: int = 3) -> str:
    """Generate context from recent chat history"""
    if not chat_history:
        return ""
    
    context = "\n\n## Recent Conversation History:\n"
    recent_chats = chat_history[-max_exchanges:]  # Get last N exchanges
    
    for i, chat in enumerate(recent_chats, 1):
        context += f"\n**Exchange {i}:**\n"
        context += f"User: {chat['user']}\n"
        context += f"Assistant: Modified the simulation code\n"
    
    context += "\n**Note:** Please consider this conversation history when making modifications to maintain consistency.\n"
    return context

def generate_requirements_with_pipreqs(code):
    """Generate requirements.txt using pipreqs like in python_runner.py"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write the code to a file
        file_path = os.path.join(temp_dir, "temp_code.py")
        with open(file_path, "w") as f:
            f.write(code)
        
        try:
            # Use pipreqs to generate requirements.txt
            subprocess.run(
                ["pipreqs", "--force", temp_dir],
                capture_output=True, text=True, timeout=30
            )
            
            # Read the generated requirements.txt
            requirements_path = os.path.join(temp_dir, "requirements.txt")
            if os.path.exists(requirements_path):
                with open(requirements_path, "r") as f:
                    return f.read()
            else:
                return "# No external dependencies detected"
                
        except Exception as e:
            return f"# Error generating requirements: {str(e)}"


def create_meaningful_filename(query, framework_choice):
    """Create a meaningful filename from the query"""
    framework_name = framework_choice.replace(' (AI)', '').lower()
    
    # Extract key words from query (remove common words)
    stop_words = {'a', 'an', 'the', 'of', 'for', 'in', 'on', 'at', 'to', 'and', 'or', 'but', 'with', 'by'}
    words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
    meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Take first 3-4 meaningful words
    filename_words = meaningful_words[:4] if len(meaningful_words) >= 4 else meaningful_words[:3]
    
    if not filename_words:
        # Fallback to framework name if no meaningful words found
        filename_base = f"{framework_name}_simulation"
    else:
        filename_base = "_".join(filename_words[:3])  # Limit to 3 words for readability
    
    # Add timestamp for uniqueness
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    
    return f"{framework_name}_{filename_base}_{timestamp}"


def create_project_export(query, config_ideas, generation_plan, generated_code, framework_choice):
    """Create a zip file containing the complete project using pipreqs"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Main code file
        framework_name = framework_choice.replace(' (AI)', '').lower()
        main_filename = f"{framework_name}_simulation.py"
        zip_file.writestr(main_filename, generated_code)
        
        # Requirements file using pipreqs (same as python_runner.py)
        requirements = generate_requirements_with_pipreqs(generated_code)
        zip_file.writestr("requirements.txt", requirements)
        
        # Project info file (this is what users will upload to load projects)
        project_info = {
            "original_query": query,
            "framework": framework_choice,
            "config_ideas": config_ideas,
            "generation_plan": generation_plan,
            "generated_code": generated_code,  # Include the actual code for loading
            "created_at": st.session_state.get("creation_timestamp", datetime.datetime.now().isoformat()),
            "version": "1.0"
        }
        zip_file.writestr("project_info.json", json.dumps(project_info, indent=2))
        
        # README file
        readme_content = f"""# {framework_choice} Simulation Project

## Original Query
{query}

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the simulation: `python {main_filename}`

## How to Load This Project Back
1. Go to the AI Simulator & Python Playground
2. In the sidebar under "Project Management", click "Load Project"
3. Upload this entire ZIP file (no need to extract!)
4. Click "Load Project Data" to restore all settings and code

## Configuration Ideas Used
{config_ideas}

## Generation Plan
{generation_plan}

## Project Structure
- `{main_filename}`: Main simulation code
- `requirements.txt`: Python dependencies (generated with pipreqs)
- `project_info.json`: Project metadata and code (for reloading in AI Simulator)
- `README.md`: This file

Generated by AI Simulator & Python Playground
"""
        zip_file.writestr("README.md", readme_content)
    
    zip_buffer.seek(0)
    return zip_buffer


def load_project_from_file(uploaded_file):
    """Load project data from uploaded ZIP or JSON file"""
    try:
        file_extension = uploaded_file.name.lower().split('.')[-1]
        
        if file_extension == 'zip':
            # Handle ZIP file - extract project_info.json
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                # Look for project_info.json in the zip
                if 'project_info.json' in zip_ref.namelist():
                    with zip_ref.open('project_info.json') as json_file:
                        project_data = json.loads(json_file.read().decode('utf-8'))
                        return project_data, "zip"
                else:
                    st.error("❌ This ZIP file doesn't contain a valid project_info.json file. Please upload a project ZIP exported from this application.")
                    return None, None
        
        elif file_extension == 'json':
            # Handle direct JSON file
            project_data = json.loads(uploaded_file.getvalue().decode('utf-8'))
            return project_data, "json"
        
        else:
            st.error("❌ Please upload either a ZIP file (exported project) or a JSON file (project_info.json).")
            return None, None
            
    except Exception as e:
        st.error(f"❌ Error loading project file: {str(e)}")
        return None, None


def display_ui():
    """
    Displays the main user interface and returns user inputs.
    """
    st.title("🤖 AI Simulator & Python Playground")

    # Create main tabs
    tab1, tab2 = st.tabs(["🔬 Create Simulation", "📚 Examples Library"])
    
    with tab2:
        # Examples Library Tab
        selected_example, selected_query, selected_code, selected_config_ideas, selected_generation_plan, generate_full_project, load_to_creation_tab = display_examples_section()
        
        if selected_example and selected_query and generate_full_project:
            # Store example data for direct display (no AI generation needed)
            st.session_state.example_query = selected_query
            st.session_state.example_code = selected_code
            st.session_state.example_filename = selected_example
            st.session_state.example_config_ideas = selected_config_ideas
            st.session_state.example_generation_plan = selected_generation_plan
            st.session_state.generate_example_project = True
    
    with tab1:
        # Main Creation Tab
        with st.sidebar:
            st.header("Configuration")
            
            st.markdown("---")
            st.info("""
            **How to use:**
            1. Configure your AI model and API key
            2. Select your desired framework
            3. Provide input via text, file, or audio
            4. Generate and run your simulation!
            """)
            st.markdown("---")
            # Model Selection (using new model selector)
            provider, model_id, api_key, model_config = display_model_selector_compact()
            
            # Framework Selection
            st.markdown("---")
            framework_choice = st.selectbox(
                "🎮 Choose Framework:", 
                ["PyGame (AI)", "Ursina (AI)"],
                help="Select the framework for your simulation"
            )
            
            st.markdown("---")
            
            # Project Management Section
            st.subheader("📁 Project Management")
            
            # Load Project with better instructions
            st.markdown("**📂 Load Existing Project**")
            st.info("💡 Upload either:\n- 📦 **Complete ZIP file** (exported project)\n- 📄 **project_info.json** file (extracted from ZIP)")
            
            uploaded_project = st.file_uploader(
                "Choose project file", 
                type=["zip", "json"], 
                help="Upload either a complete project ZIP file or just the project_info.json file"
            )
            
            if uploaded_project:
                project_data, file_type = load_project_from_file(uploaded_project)
                if project_data:
                    # Show project preview
                    with st.expander("📋 Project Preview", expanded=True):
                        st.write(f"**File Type:** {file_type.upper()}")
                        st.write(f"**Framework:** {project_data.get('framework', 'Unknown')}")
                        st.write(f"**Created:** {project_data.get('created_at', 'Unknown')}")
                        st.write(f"**Query:** {project_data.get('original_query', 'No query')[:100]}...")
                    
                    if st.button("🔄 Load Project Data", type="primary"):
                        # Load all project data into session state
                        st.session_state.loaded_query = project_data.get("original_query", "")
                        st.session_state.config_ideas = project_data.get("config_ideas", "")
                        st.session_state.generation_plan = project_data.get("generation_plan", "")
                        st.session_state.generated_code = project_data.get("generated_code", "")
                        st.session_state.playground_code = project_data.get("generated_code", "")
                        st.session_state.show_playground = True
                        
                        # Store creation timestamp
                        st.session_state.creation_timestamp = project_data.get("created_at", datetime.datetime.now().isoformat())
                        
                        # Update framework choice if different
                        loaded_framework = project_data.get("framework", framework_choice)
                        if loaded_framework != framework_choice:
                            st.warning(f"⚠️ Project was created with {loaded_framework}. Please change the framework selection above.")
                        
                        st.success("✅ Project loaded successfully!")
                        st.rerun()
            
        # Check if model is configured
        if not model_config or not api_key:
            st.warning("⚠️ Please configure your AI model in the sidebar to continue.")
            st.stop()

        # --- AI Generation Mode ---
        framework_name = framework_choice.replace(' (AI)', '')

        input_mode = st.radio("Input Mode", ["Text", "File Upload", "Audio Upload", "Audio Recording"])

        query = ""
        uploaded_file = None
        uploaded_audio = None
        
        # Check if we have loaded project data
        if "loaded_query" in st.session_state and st.session_state.loaded_query:
            query = st.session_state.loaded_query
            st.info("📂 Using query from loaded project. You can modify it below.")
            del st.session_state.loaded_query  # Clear the loaded query
        
        # Check if we have an example query
        elif "example_query" in st.session_state and st.session_state.example_query:
            query = st.session_state.example_query
            st.info("📚 Using query from examples library. You can modify it below.")
        
        if input_mode == "Text":
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                query = st.text_area(
                    f"Describe the {framework_name} simulation you want to create:",
                    height=100,
                    placeholder=f"e.g., A simple {framework_name} simulation of bouncing balls...",
                    key="query_text",
                    value=query
                )
            with col2:
                st.write("") # for alignment
                st.write("") # for alignment
                copy_button(st.session_state.get("query_text", ""), key = "Copy Query")
                
        elif input_mode == "File Upload":
            uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "csv", "docx"])
            if uploaded_file:
                st.success("File uploaded successfully. Will be used as input query.")
                try:
                    query = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                except:
                    query = "File uploaded but couldn't extract text content."
                
        elif input_mode == "Audio Upload":
            st.write(f"🎤 Upload audio file for your {framework_name} simulation query:")
            uploaded_audio = st.file_uploader("Upload Audio File", type=["wav", "mp3", "m4a"])

            if uploaded_audio is not None:
                # Display audio player
                st.audio(uploaded_audio)
                
                # Auto-trigger transcription
                if f"transcribed_{uploaded_audio.name}" not in st.session_state:
                    with st.spinner("🎯 Transcribing audio automatically..."):
                        transcribed_text, chunk_results = transcribe_audio(uploaded_audio)
                        st.session_state[f"transcribed_{uploaded_audio.name}"] = transcribed_text
                        st.session_state[f"chunks_{uploaded_audio.name}"] = chunk_results
                        st.success("Transcription completed!")
                        st.rerun()
                
                # Get transcribed text from session state
                if f"transcribed_{uploaded_audio.name}" in st.session_state:
                    query = st.session_state[f"transcribed_{uploaded_audio.name}"]
                    
                    # Show chunk results in expandable section
                    if f"chunks_{uploaded_audio.name}" in st.session_state:
                        chunk_results = st.session_state[f"chunks_{uploaded_audio.name}"]
                        with st.expander(f"📄 Transcription Details ({len(chunk_results)} chunks)", expanded=False):
                            for chunk_info in chunk_results:
                                if chunk_info["status"] == "success":
                                    st.success(f"Chunk {chunk_info['chunk']}: {chunk_info['text']}")
                                elif chunk_info["status"] == "warning":
                                    st.warning(f"Chunk {chunk_info['chunk']}: {chunk_info['text']}")
                                else:
                                    st.error(f"Chunk {chunk_info['chunk']}: {chunk_info['text']}")
                    
                    # Display and allow editing of transcribed text
                    query = st.text_area(
                        "Transcribed Query (you can edit this):", 
                        value=query, 
                        height=100, 
                        key="transcribed_query_edit"
                    )
                    
        elif input_mode == "Audio Recording":
            st.write(f"🎤 Record audio for your {framework_name} simulation query:")
            recorded_audio = st.audio_input("Record your audio query")

            if recorded_audio is not None:
                # Display recorded audio player
                st.audio(recorded_audio)
                
                # Auto-trigger transcription
                audio_key = f"recorded_{hash(recorded_audio)}"
                if audio_key not in st.session_state:
                    with st.spinner("🎯 Transcribing recorded audio automatically..."):
                        transcribed_text, chunk_results = transcribe_audio(recorded_audio)
                        st.session_state[audio_key] = transcribed_text
                        st.session_state[f"chunks_{audio_key}"] = chunk_results
                        st.success("Transcription completed!")
                        st.rerun()
                
                # Get transcribed text from session state
                if audio_key in st.session_state:
                    query = st.session_state[audio_key]
                    
                    # Show chunk results in expandable section
                    if f"chunks_{audio_key}" in st.session_state:
                        chunk_results = st.session_state[f"chunks_{audio_key}"]
                        with st.expander(f"📄 Transcription Details ({len(chunk_results)} chunks)", expanded=False):
                            for chunk_info in chunk_results:
                                if chunk_info["status"] == "success":
                                    st.success(f"Chunk {chunk_info['chunk']}: {chunk_info['text']}")
                                elif chunk_info["status"] == "warning":
                                    st.warning(f"Chunk {chunk_info['chunk']}: {chunk_info['text']}")
                                else:
                                    st.error(f"Chunk {chunk_info['chunk']}: {chunk_info['text']}")
                    
                    # Display and allow editing of transcribed text
                    query = st.text_area(
                        "Transcribed Query (you can edit this):", 
                        value=query, 
                        height=100, 
                        key="recorded_transcribed_query_edit"
                    )

        start_action = st.button(f"✨ Generate {framework_name} Code")
        run_in_playground = False

        # Auto-generate example project if flag is set
        if st.session_state.get("generate_example_project", False):
            start_action = True
            # Clear the flag to prevent repeated generation
            st.session_state.generate_example_project = False

        # --- Display Generation Results ---
        if "config_ideas" in st.session_state:
            with st.expander("⚙️ Configuration Ideas", expanded=False):
                st.write(st.session_state.config_ideas)

        if "generation_plan" in st.session_state:
            with st.expander("📝 Generation Plan", expanded=False):
                st.write(st.session_state.generation_plan)

        # Auto-collapse code expander after generation
        code_expanded = st.session_state.get("show_generated_code", True)
        if "generated_code" in st.session_state and st.session_state.get("code_just_generated", False):
            code_expanded = False
            st.session_state.show_generated_code = False
            st.session_state.code_just_generated = False

        if "generated_code" in st.session_state:
            with st.expander(f"Generated {framework_name} Code", expanded=code_expanded):
                col1_code, col2_code = st.columns([0.9, 0.1])
                with col1_code:
                    st.session_state.generated_code = st_ace(
                        value=st.session_state.generated_code,
                        language="python",
                        theme="monokai",
                        keybinding="vscode",
                        height=300,
                        key="generated_code_editor"
                    )
                with col2_code:
                    st.write("")
                    st.write("")
                    copy_button(st.session_state.generated_code, key = "Copy Code")

            # Action buttons row
            col1, col2, col3, col4, col5, col6 = st.columns([0.17, 0.17, 0.16, 0.17, 0.16, 0.17])
            
            with col1:
                if st.button("🚀 Open in Playground", type="primary"):
                    st.session_state.show_playground = True
                    st.session_state.playground_code = st.session_state.generated_code
                    st.rerun()
            
            with col2:
                if st.button("📖 Explain Code"):
                    if "code_explanation" not in st.session_state:
                        with st.spinner("🤖 Generating code explanation..."):
                            explanation = explain_code(
                                st.session_state.generated_code, 
                                model_config, 
                                framework_choice
                            )
                            st.session_state.code_explanation = explanation
                    st.session_state.show_explanation = True
                    st.rerun()
            with col3:
                if st.button("🎓 Learn Concepts"):
                    if "learning_content" not in st.session_state:
                        with st.spinner("🎓 Generating learning materials..."):
                            from agents.learning_agent import LearningAgent
                            learning_agent = LearningAgent(model_config, framework_choice)
                            learning_content = learning_agent.generate_learning_content(
                                st.session_state.generated_code,
                                query,
                                st.session_state.get('config_ideas'),
                                st.session_state.get('generation_plan')
                            )
                            st.session_state.learning_content = learning_content
                    st.session_state.show_learning = True
                    st.rerun()

            with col4:
                # Add to Gallery button
                if st.button("📚 Add to Gallery"):
                    if all(key in st.session_state for key in ["config_ideas", "generation_plan", "generated_code"]):
                        # Show a form to customize the example entry
                        st.session_state.show_gallery_form = True
                        st.rerun()
                    else:
                        st.warning("Complete project data not available for adding to gallery.")
            
            with col5:
                # Export project button with improved naming
                if st.button("📦 Export Project"):
                    if all(key in st.session_state for key in ["config_ideas", "generation_plan", "generated_code"]):
                        # Create meaningful filename
                        meaningful_name = create_meaningful_filename(query, framework_choice)
                        
                        zip_buffer = create_project_export(
                            query,
                            st.session_state.config_ideas,
                            st.session_state.generation_plan,
                            st.session_state.generated_code,
                            framework_choice
                        )
                        
                        st.download_button(
                            label="📥 Download Project Zip",
                            data=zip_buffer.getvalue(),
                            file_name=f"{meaningful_name}.zip",
                            mime="application/zip",
                            help="Complete project folder - can be uploaded directly to load later!"
                        )
                    else:
                        st.warning("Complete project data not available for export.")
            
            with col6:
                # Save project button with improved naming
                if st.button("💾 Save Project"):
                    if all(key in st.session_state for key in ["config_ideas", "generation_plan", "generated_code"]):
                        # Create meaningful filename
                        meaningful_name = create_meaningful_filename(query, framework_choice)
                        
                        project_data = {
                            "original_query": query,
                            "framework": framework_choice,
                            "config_ideas": st.session_state.config_ideas,
                            "generation_plan": st.session_state.generation_plan,
                            "generated_code": st.session_state.generated_code,
                            "created_at": st.session_state.get("creation_timestamp", datetime.datetime.now().isoformat()),
                            "version": "1.0"
                        }
                        
                        st.download_button(
                            label="📁 Download Project File",
                            data=json.dumps(project_data, indent=2),
                            file_name=f"{meaningful_name}_project.json",
                            mime="application/json",
                            help="JSON file that can be uploaded to restore this project"
                        )
                    else:
                        st.warning("Complete project data not available for saving.")

            # Gallery form modal
            if st.session_state.get("show_gallery_form", False):
                with st.expander("📚 Add to Examples Gallery", expanded=True):
                    st.markdown("### Customize Your Example Entry")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        custom_title = st.text_input(
                            "Example Title:",
                            value=f"🔬 {' '.join(query.split()[:4]).title()} Simulation",
                            help="Give your example a descriptive title"
                        )
                        
                        custom_difficulty = st.selectbox(
                            "Difficulty Level:",
                            ["Beginner", "Intermediate", "Advanced"],
                            index=1,
                            help="How complex is this simulation?"
                        )
                    
                    with col2:
                        # Generate default description from config_ideas
                        default_desc = st.session_state.config_ideas.split('.')[0] if st.session_state.config_ideas else query
                        if len(default_desc) > 150:
                            default_desc = default_desc[:150] + "..."
                        
                        custom_description = st.text_area(
                            "Description:",
                            value=default_desc,
                            height=100,
                            help="Brief description of what this simulation does"
                        )
                    
                    # Preview
                    st.markdown("#### 📋 Preview:")
                    st.info(f"**{custom_title}** - {custom_difficulty}\n\n{custom_description}")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✅ Add to Gallery", type="primary"):
                            success, filename = add_to_examples_gallery(
                                query,
                                st.session_state.config_ideas,
                                st.session_state.generation_plan,
                                st.session_state.generated_code,
                                framework_choice,
                                custom_title,
                                custom_description,
                                custom_difficulty
                            )
                            
                            if success:
                                st.success(f"🎉 Successfully added '{custom_title}' to the examples gallery!")
                                st.info(f"📁 Saved as: {filename}")
                                st.session_state.show_gallery_form = False
                                st.balloons()
                            else:
                                st.error("❌ Failed to add example to gallery. Please try again.")
                    
                    with col2:
                        if st.button("❌ Cancel"):
                            st.session_state.show_gallery_form = False
                            st.rerun()
                    
                    with col3:
                        st.write("") 
            
            # Code explanation section
            if st.session_state.get("show_explanation", False):
                with st.expander(f"📖 Code Explanation", expanded=True):
                    if "code_explanation" in st.session_state:
                        st.markdown(st.session_state.code_explanation)
                        
                        col1, col2 = st.columns([0.9, 0.1])
                        with col2:
                            if st.button("❌", help="Close Explanation"):
                                st.session_state.show_explanation = False
                                st.rerun()

            # Learning content section
            if st.session_state.get("show_learning", False):
                with st.expander(f"🎓 Learning Materials", expanded=True):
                    if "learning_content" in st.session_state:
                        st.markdown(st.session_state.learning_content)
                        
                        col1, col2 = st.columns([0.9, 0.1])
                        with col2:
                            if st.button("❌", help="Close Learning Materials", key="close_learning"):
                                st.session_state.show_learning = False
                                st.rerun()

        # --- Python Playground Section (Before Chat) ---
        if st.session_state.get("show_playground", False):
            st.markdown("---")
            
            # Playground header with close button
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.subheader("🐍 Python Playground")
            with col2:
                if st.button("❌", help="Close Playground"):
                    st.session_state.show_playground = False
                    st.rerun()
            
            # Tabs for better organization
            tab1, tab2 = st.tabs(["📝 Code Editor", "🖥️ Output"])
            
            with tab1:
                st.session_state.playground_code = st_ace(
                    value=st.session_state.get("playground_code", ""),
                    language="python",
                    theme="monokai",
                    keybinding="vscode",
                    height=400,
                    key="playground_editor"
                )
                
                col1, col2, col3 = st.columns([0.3, 0.3, 0.4])
                with col1:
                    run_in_playground = st.button("▶️ Run Code", type="primary")
                with col2:
                    if st.button("💾 Save to Generated"):
                        st.session_state.generated_code = st.session_state.playground_code
                        st.success("Code saved to generated code!")
                with col3:
                    copy_button(st.session_state.get("playground_code", ""), key="Copy Playground Code")
            
            with tab2:
                if "python_output" in st.session_state:
                    st.markdown("**Output:**")
                    st.code(st.session_state.python_output, language="bash")
                if "python_error" in st.session_state and st.session_state.python_error:
                    st.markdown("**Error:**")
                    st.error(st.session_state.python_error)
                
                if not st.session_state.get("python_output") and not st.session_state.get("python_error"):
                    st.info("🚀 Click 'Run Code' in the Code Editor tab to see output here")

        # --- Chat for Modifications (After Playground) ---
        if "generated_code" in st.session_state:
            st.markdown("---")
            st.subheader("💬 Chat with AI Assistant")

            # Initialize chat history if it doesn't exist
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            # Display chat history with updated code in expandable format
            # Only show if there's actual chat history
            if st.session_state.chat_history:
                for i, chat in enumerate(st.session_state.chat_history):
                    # User message
                    with st.chat_message("user"):
                        st.write(chat['user'])
                    
                    # Assistant message with context info
                    with st.chat_message("assistant"):
                        # Show context information in an expandable section
                        with st.expander("📋 Context Used", expanded=False):
                            col1, col2 = st.columns(2)
                            with col1:
                                if "config_ideas" in st.session_state:
                                    st.markdown("**⚙️ Configuration Ideas:**")
                                    st.text(st.session_state.config_ideas[:200] + "..." if len(st.session_state.config_ideas) > 200 else st.session_state.config_ideas)
                            with col2:
                                if "generation_plan" in st.session_state:
                                    st.markdown("**📝 Generation Plan:**")
                                    st.text(st.session_state.generation_plan[:200] + "..." if len(st.session_state.generation_plan) > 200 else st.session_state.generation_plan)
                        
                        # Show updated code in expandable format (like the original generated code)
                        with st.expander(f"Updated {framework_name} Code - Version {i+1}", expanded=False):
                            col1_chat_code, col2_chat_code = st.columns([0.9, 0.1])
                            with col1_chat_code:
                                st_ace(
                                    value=chat['code'],
                                    language="python",
                                    theme="monokai",
                                    keybinding="vscode",
                                    height=300,
                                    key=f"chat_code_editor_{i}",
                                    readonly=True
                                )
                            with col2_chat_code:
                                st.write("")
                                st.write("")
                                copy_button(chat['code'], key=f"Copy Chat Code {i}")
                        
                        # Button to update playground with this version (always show for all versions)
                        if st.button(f"🔄 Load Version {i+1} to Playground", key=f"load_chat_{i}"):
                            st.session_state.playground_code = chat['code']
                            st.session_state.show_playground = True
                            st.success(f"Version {i+1} loaded to playground!")
                            st.rerun()
            else:
                # Show a message when no chat history exists
                st.info("💡 Start a conversation to modify your simulation! Ask for changes, improvements, or new features.")

            # Chat input with enhanced context
            if mod_query := st.chat_input("Request a modification to your simulation..."):
                # Add user message to chat
                with st.chat_message("user"):
                    st.write(mod_query)
                
                # Generate response
                with st.chat_message("assistant"):
                    with st.spinner("🤖 Updating simulation..."):
                        from agents.code_gen_agent import CodeGenAgent
                        code_generator = CodeGenAgent(model_config, framework_choice)
                        
                        # Get conversation context
                        chat_context = get_chat_context(st.session_state.chat_history)
                        
                        # Create comprehensive modification prompt
                        modification_context = f"""
                        IMPORTANT: Generate a COMPLETE, FULL, RUNNABLE Python script. Do not provide just code snippets or partial code.
                        
                        ## Original Project Context:
                        **Original Request:** {query}
                        
                        **Configuration Ideas Used:**
                        {st.session_state.get('config_ideas', 'None')}
                        
                        **Generation Plan:**
                        {st.session_state.get('generation_plan', 'None')}
                        
                        ## Current Code:
                        ```python
                        {st.session_state.get('playground_code', st.session_state.get('generated_code', ''))}
                        ```
                        
                        {chat_context}
                        
                        ## Current Modification Request:
                        {mod_query}
                        
                        ## Instructions:
                        1. Analyze the conversation history to understand previous modifications
                        2. Apply the new modification while maintaining consistency
                        3. Return the COMPLETE, FULL, RUNNABLE Python script
                        4. Ensure all previous features and modifications are preserved unless explicitly changed
                        """
                        
                        new_code = code_generator.generate_code(
                            modification_context,
                            error_feedback=f"Modify the existing COMPLETE code considering conversation history. Request: {mod_query}. Return the full, complete, runnable script.",
                            file=uploaded_file,
                            audio=uploaded_audio
                        )
                    
                    # Show context information
                    with st.expander("📋 Context Used", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            if "config_ideas" in st.session_state:
                                st.markdown("**⚙️ Configuration Ideas:**")
                                st.text(st.session_state.config_ideas[:200] + "..." if len(st.session_state.config_ideas) > 200 else st.session_state.config_ideas)
                        with col2:
                            if "generation_plan" in st.session_state:
                                st.markdown("**📝 Generation Plan:**")
                                st.text(st.session_state.generation_plan[:200] + "..." if len(st.session_state.generation_plan) > 200 else st.session_state.generation_plan)
                        
                        # Show conversation context
                        if st.session_state.chat_history:
                            st.markdown("**💬 Recent Conversation:**")
                            for i, chat in enumerate(st.session_state.chat_history[-2:], 1):
                                st.text(f"{i}. User: {chat['user'][:100]}...")
                    
                    # Show updated code in expandable format
                    new_version_number = len(st.session_state.chat_history) + 1
                    with st.expander(f"Updated {framework_name} Code - Version {new_version_number}", expanded=True):
                        col1_new_code, col2_new_code = st.columns([0.9, 0.1])
                        with col1_new_code:
                            st_ace(
                                value=new_code,
                                language="python",
                                theme="monokai",
                                keybinding="vscode",
                                height=300,
                                key=f"new_chat_code_editor_{new_version_number}",
                                readonly=True
                            )
                        with col2_new_code:
                            st.write("")
                            st.write("")
                            copy_button(new_code, key=f"Copy New Chat Code {new_version_number}")
                    
                    # Load button for the new version
                    if st.button(f"🔄 Load Version {new_version_number} to Playground", key=f"load_new_chat_{new_version_number}"):
                        st.session_state.playground_code = new_code
                        st.session_state.show_playground = True
                        st.success(f"Version {new_version_number} loaded to playground!")
                        st.rerun()
                    
                    # Auto-update playground with the most recent code
                    st.session_state.playground_code = new_code
                    st.session_state.generated_code = new_code
                    
                    # Automatically open playground if not already open
                    if not st.session_state.get("show_playground", False):
                        st.session_state.show_playground = True
                    
                    st.success("✅ Complete code automatically updated in playground!")
                
                # Add to chat history with metadata
                st.session_state.chat_history.append({
                    "user": mod_query, 
                    "code": new_code,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "version": len(st.session_state.chat_history) + 1
                })
                st.rerun()

        return query, provider, model_config, framework_choice, start_action, run_in_playground, uploaded_file, uploaded_audio