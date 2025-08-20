import streamlit as st
import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import shutil
import datetime

class ExamplesLibrary:
    """Handles the examples library UI and functionality"""
    
    def __init__(self):
        self.examples_dir = Path("examples")
        self.examples_metadata_file = Path("ui/examples_metadata.json")
        self.load_examples_metadata()
    
    def load_examples_metadata(self):
        """Load examples metadata from JSON file"""
        try:
            if self.examples_metadata_file.exists():
                with open(self.examples_metadata_file, 'r') as f:
                    self.examples_metadata = json.load(f)
            else:
                self.examples_metadata = self.generate_default_metadata()
                self.save_examples_metadata()
        except Exception as e:
            st.error(f"Error loading examples metadata: {e}")
            self.examples_metadata = self.generate_default_metadata()
    
    def save_examples_metadata(self):
        """Save examples metadata to JSON file"""
        try:
            os.makedirs(self.examples_metadata_file.parent, exist_ok=True)
            with open(self.examples_metadata_file, 'w') as f:
                json.dump(self.examples_metadata, f, indent=2)
        except Exception as e:
            st.error(f"Error saving examples metadata: {e}")
    
    def add_example_to_gallery(self, query: str, config_ideas: str, generation_plan: str, 
                              generated_code: str, framework_choice: str, 
                              custom_title: str = None, custom_description: str = None,
                              custom_difficulty: str = "Intermediate") -> bool:
        """Add a new example to the gallery"""
        try:
            # Create filename from title or query
            if custom_title:
                # Clean up title for filename
                filename_base = custom_title.lower()
                filename_base = ''.join(c if c.isalnum() or c == ' ' else '' for c in filename_base)
                filename_base = '_'.join(filename_base.split())
            else:
                # Generate from query
                words = query.lower().split()[:3]  # Take first 3 words
                filename_base = '_'.join(word.strip('.,!?') for word in words if word.strip('.,!?'))
            
            # Add timestamp to ensure uniqueness
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{filename_base}_{timestamp}.py"
            
            # Ensure examples directory exists
            os.makedirs(self.examples_dir, exist_ok=True)
            
            # Write code to file
            code_path = self.examples_dir / filename
            with open(code_path, 'w') as f:
                f.write(generated_code)
            
            # Extract features from config_ideas and generation_plan
            features = self.extract_features_from_text(config_ideas, generation_plan)
            
            # Create metadata entry
            framework_name = framework_choice.replace(' (AI)', '')
            
            # Generate title and description if not provided
            if not custom_title:
                custom_title = f"🔬 {' '.join(query.split()[:4]).title()} Simulation"
            
            if not custom_description:
                # Extract first sentence from config_ideas or use query
                first_sentence = config_ideas.split('.')[0] if config_ideas else query
                custom_description = first_sentence[:150] + "..." if len(first_sentence) > 150 else first_sentence
            
            new_metadata = {
                "title": custom_title,
                "description": custom_description,
                "framework": framework_name,
                "difficulty": custom_difficulty,
                "features": features,
                "query": query,
                "config_ideas": config_ideas,
                "generation_plan": generation_plan,
                "created_at": datetime.datetime.now().isoformat(),
                "user_generated": True  # Flag to identify user-generated examples
            }
            
            # Add to metadata
            self.examples_metadata[filename] = new_metadata
            
            # Save metadata
            self.save_examples_metadata()
            
            return True, filename
            
        except Exception as e:
            st.error(f"Error adding example to gallery: {e}")
            return False, None
    
    def extract_features_from_text(self, config_ideas: str, generation_plan: str) -> List[str]:
        """Extract key features from config ideas and generation plan"""
        combined_text = f"{config_ideas} {generation_plan}".lower()
        
        # Common feature keywords to look for
        feature_keywords = {
            "interactive": "Interactive controls",
            "slider": "Interactive sliders", 
            "physics": "Physics simulation",
            "collision": "Collision detection",
            "particle": "Particle system",
            "gravity": "Gravity effects",
            "force": "Force visualization",
            "energy": "Energy calculations",
            "vector": "Vector visualization",
            "friction": "Friction effects",
            "momentum": "Momentum conservation",
            "real-time": "Real-time updates",
            "3d": "3D graphics",
            "animation": "Animation effects",
            "ui": "User interface",
            "control": "User controls",
            "simulation": "Simulation engine",
            "visualization": "Data visualization"
        }
        
        features = []
        for keyword, feature in feature_keywords.items():
            if keyword in combined_text and feature not in features:
                features.append(feature)
        
        # Limit to 6 features max
        return features[:6] if features else ["Custom simulation", "Interactive features"]
    
    def delete_example_from_gallery(self, filename: str) -> bool:
        """Delete an example from the gallery (only user-generated ones)"""
        try:
            if filename not in self.examples_metadata:
                return False
            
            # Only allow deletion of user-generated examples
            if not self.examples_metadata[filename].get("user_generated", False):
                st.error("❌ Cannot delete built-in examples. Only user-generated examples can be deleted.")
                return False
            
            # Delete code file
            code_path = self.examples_dir / filename
            if code_path.exists():
                os.remove(code_path)
            
            # Remove from metadata
            del self.examples_metadata[filename]
            
            # Save metadata
            self.save_examples_metadata()
            
            return True
            
        except Exception as e:
            st.error(f"Error deleting example: {e}")
            return False
    
    def generate_default_metadata(self) -> Dict:
        """Generate default metadata for examples"""
        return {
            "balls_dropping.py": {
                "title": "🏀 Bouncing Balls Simulation",
                "description": "Interactive physics simulation with bouncing balls. Control restitution, mass, gravity, and ground properties.",
                "framework": "PyGame",
                "difficulty": "Intermediate",
                "features": [
                    "Physics simulation",
                    "Interactive sliders",
                    "Ground angle adjustment",
                    "Ball-to-ball collisions",
                    "Elasticity controls"
                ],
                "query": "Create a bouncing balls simulation where balls fall and bounce with adjustable physics parameters like restitution, mass, gravity, and ground angle",
                "config_ideas": "Interactive simulation with adjustable physics parameters including ball restitution (0.3-0.9), ball mass (1-5 kg), gravity strength (50-500), and ground angle (-30° to 30°). Features multiple colored balls with realistic collision physics, energy visualization, and real-time parameter adjustment through sliders.",
                "generation_plan": "Create a PyGame simulation with: 1) Ball class with physics properties (position, velocity, mass, restitution), 2) Physics engine for gravity and collision detection, 3) Interactive UI with sliders for real-time parameter adjustment, 4) Visual feedback with energy indicators and collision highlights, 5) Ground surface with adjustable angle affecting ball behavior.",
                "user_generated": False
            },
            "billard_balls.py": {
                "title": "🎱 Billard Balls Physics",
                "description": "Advanced particle system with realistic ball physics, gravity controls, and force interactions.",
                "framework": "PyGame",
                "difficulty": "Advanced",
                "features": [
                    "Particle system",
                    "Force application",
                    "Gravity controls",
                    "UI sliders",
                    "Collision highlighting"
                ],
                "query": "Create a billiard-like simulation with particle physics where balls respond to gravity and force interactions",
                "config_ideas": "Advanced particle physics system with billiard ball dynamics including elastic collisions, momentum conservation, friction effects, and interactive force application. Features adjustable gravity, ball-to-ball interactions, energy dissipation, and visual force vectors for educational physics demonstration.",
                "generation_plan": "Develop a sophisticated PyGame billiards simulation featuring: 1) Particle system with multiple balls having realistic physics properties, 2) Advanced collision detection and response with momentum conservation, 3) Interactive controls for applying forces and adjusting gravity, 4) Visual feedback systems showing velocity vectors and collision effects, 5) UI controls for real-time physics parameter modification.",
                "user_generated": False
            },
            "collision_box_wall.py": {
                "title": "📦 Box-Wall Collision",
                "description": "Newton's 3rd law demonstration with box-wall collisions, showing forces, impulse, and energy calculations.",
                "framework": "PyGame",
                "difficulty": "Intermediate",
                "features": [
                    "Collision physics",
                    "Force visualization",
                    "Interactive sliders",
                    "Energy calculations",
                    "Impulse display"
                ],
                "query": "Create a physics simulation demonstrating Newton's 3rd law with a box colliding against a wall, showing force vectors and impulse calculations",
                "config_ideas": "Educational physics simulation demonstrating Newton's third law through box-wall collisions with real-time force vector visualization, impulse calculations, and energy transfer analysis. Interactive controls for box mass, velocity, wall restitution, and collision timing with detailed mathematical feedback.",
                "generation_plan": "Build a PyGame physics demonstration with: 1) Box object with configurable mass and velocity properties, 2) Wall surface with adjustable restitution coefficient, 3) Real-time force vector visualization during collisions, 4) Mathematical calculations display for impulse, momentum change, and energy transfer, 5) Interactive parameter controls with immediate visual feedback.",
                "user_generated": False
            },
            "newtons3rd_law.py": {
                "title": "⚖️ Newton's Third Law Demo",
                "description": "Comprehensive demonstration of Newton's third law with interactive controls and real-time physics calculations.",
                "framework": "PyGame",
                "difficulty": "Advanced",
                "features": [
                    "Newton's laws simulation",
                    "Interactive sliders",
                    "Force vectors",
                    "Energy calculations",
                    "Friction effects"
                ],
                "query": "Create a comprehensive Newton's third law simulation with interactive controls for mass, velocity, friction, and restitution",
                "config_ideas": "Comprehensive Newton's third law educational simulation featuring interactive objects with adjustable mass, velocity, friction coefficients, and restitution values. Real-time visualization of action-reaction force pairs, energy conservation principles, and momentum transfer with detailed mathematical analysis and parameter exploration.",
                "generation_plan": "Create an advanced PyGame physics education tool with: 1) Multiple interactive objects demonstrating Newton's third law, 2) Comprehensive force vector visualization system, 3) Real-time mathematical calculations for forces, momentum, and energy, 4) Interactive parameter adjustment interface with sliders, 5) Educational overlays explaining physics principles and mathematical relationships.",
                "user_generated": False
            }
        }
    
    def get_example_code(self, filename: str) -> Optional[str]:
        """Read example code from file"""
        try:
            example_path = self.examples_dir / filename
            if example_path.exists():
                with open(example_path, "r") as f:
                    return f.read()
            return None
        except Exception as e:
            st.error(f"Error reading example file {filename}: {e}")
            return None
    
    def get_example_complete_data(self, filename: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Get complete example data: query, config_ideas, generation_plan, code"""
        if filename not in self.examples_metadata:
            return None, None, None, None
        
        metadata = self.examples_metadata[filename]
        query = metadata.get('query', '')
        config_ideas = metadata.get('config_ideas', '')
        generation_plan = metadata.get('generation_plan', '')
        code = self.get_example_code(filename)
        
        return query, config_ideas, generation_plan, code
    
    def get_difficulty_color(self, difficulty: str) -> str:
        """Get color for difficulty level"""
        colors = {
            "Beginner": "🟢",
            "Intermediate": "🟡", 
            "Advanced": "🔴"
        }
        return colors.get(difficulty, "⚪")
    
    def get_framework_icon(self, framework: str) -> str:
        """Get icon for framework"""
        icons = {
            "PyGame": "🎮",
            "Ursina": "🎲"
        }
        return icons.get(framework, "🔧")
    
    def display_examples_library(self) -> tuple:
        """Display the examples library UI"""
        st.markdown("## 📚 Examples Library")
        st.markdown("Explore pre-built simulations and learn from working examples!")
        
        # Filter controls with user-generated filter
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            framework_filter = st.selectbox(
                "Filter by Framework:",
                ["All", "PyGame", "Ursina"],
                key="examples_framework_filter"
            )
        
        with col2:
            difficulty_filter = st.selectbox(
                "Filter by Difficulty:",
                ["All", "Beginner", "Intermediate", "Advanced"],
                key="examples_difficulty_filter"
            )
        
        with col3:
            source_filter = st.selectbox(
                "Filter by Source:",
                ["All", "Built-in", "User-generated"],
                key="examples_source_filter"
            )
        
        with col4:
            search_term = st.text_input(
                "🔍 Search examples:",
                placeholder="Type to search...",
                key="examples_search"
            )
        
        # Filter examples
        filtered_examples = self.filter_examples(framework_filter, difficulty_filter, search_term, source_filter)
        
        if not filtered_examples:
            st.info("No examples match your filters. Try adjusting the criteria.")
            return None, None, None, None, None, None, None
        
        # Show stats
        total_examples = len(self.examples_metadata)
        user_generated = sum(1 for meta in self.examples_metadata.values() if meta.get("user_generated", False))
        built_in = total_examples - user_generated
        
        st.info(f"📊 **Gallery Stats:** {total_examples} total examples ({built_in} built-in, {user_generated} user-generated)")
        
        # Display examples in cards
        selected_example = None
        selected_query = None
        selected_code = None
        selected_config_ideas = None
        selected_generation_plan = None
        generate_full_project = False
        load_to_creation_tab = False
        
        for filename, metadata in filtered_examples.items():
            with st.container():
                # Create card layout
                card_col1, card_col2, card_col3 = st.columns([0.55, 0.25, 0.2])
                
                with card_col1:
                    # Add user-generated badge
                    title = metadata['title']
                    if metadata.get('user_generated', False):
                        title += " 👤"
                    st.markdown(f"### {title}")
                    st.markdown(f"*{metadata['description']}*")
                    
                    # Features display
                    if metadata.get('features'):
                        features_text = " • ".join(metadata['features'][:3])
                        if len(metadata['features']) > 3:
                            features_text += f" • +{len(metadata['features'])-3} more"
                        st.markdown(f"**Features:** {features_text}")
                
                with card_col2:
                    st.markdown(f"{self.get_framework_icon(metadata['framework'])} **{metadata['framework']}**")
                    st.markdown(f"{self.get_difficulty_color(metadata['difficulty'])} {metadata['difficulty']}")
                    
                    # Show creation date for user-generated
                    if metadata.get('user_generated', False) and metadata.get('created_at'):
                        created_date = metadata['created_at'][:10]  # Just the date part
                        st.markdown(f"📅 {created_date}")
                
                with card_col3:
                    # Action buttons
                    if st.button("👁️ View", key=f"view_{filename}"):
                        # Toggle view state for this specific example
                        current_state = st.session_state.get(f"show_details_{filename}", False)
                        st.session_state[f"show_details_{filename}"] = not current_state
                        st.rerun()
                    
                    if st.button("🚀 Load", key=f"load_{filename}", type="primary"):
                        selected_example = filename
                        # Get complete data including pre-generated config and plan
                        query, config_ideas, generation_plan, code = self.get_example_complete_data(filename)
                        selected_query = query
                        selected_code = code
                        selected_config_ideas = config_ideas
                        selected_generation_plan = generation_plan
                        generate_full_project = True
                        load_to_creation_tab = True
                    
                    # Delete button for user-generated examples
                    if metadata.get('user_generated', False):
                        if st.button("🗑️", key=f"delete_{filename}", help="Delete this example"):
                            if st.session_state.get(f"confirm_delete_{filename}", False):
                                if self.delete_example_from_gallery(filename):
                                    st.success(f"✅ Deleted example: {metadata['title']}")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete example")
                            else:
                                st.session_state[f"confirm_delete_{filename}"] = True
                                st.warning("⚠️ Click delete again to confirm")
                                st.rerun()
                
                # Show inline example details if toggled
                if st.session_state.get(f"show_details_{filename}", False):
                    self.display_example_details_inline(filename, metadata)
                
                # Show success messages right below the clicked example
                if selected_example == filename and load_to_creation_tab:
                    st.success("✅ Example loaded! Switch to 'Create Simulation' tab to see it.")
                    st.info("💡 All example data loaded directly - no AI generation needed!")
                
                st.markdown("---")
        
        return selected_example, selected_query, selected_code, selected_config_ideas, selected_generation_plan, generate_full_project, load_to_creation_tab
    
    def display_example_details_inline(self, filename: str, metadata: Dict):
        """Display example details inline below the card"""
        with st.container():
            st.markdown("##### 📖 Example Details")
            
            col1, col2 = st.columns([0.7, 0.3])
            
            with col1:
                st.markdown(f"**Description:** {metadata['description']}")
                
                if metadata.get('features'):
                    st.markdown("**Features:**")
                    for feature in metadata['features']:
                        st.markdown(f"• {feature}")
                
                # Show pre-generated data if available
                if metadata.get('config_ideas'):
                    with st.expander("⚙️ Configuration Ideas", expanded=False):
                        st.write(metadata['config_ideas'])
                
                if metadata.get('generation_plan'):
                    with st.expander("📝 Generation Plan", expanded=False):
                        st.write(metadata['generation_plan'])
            
            with col2:
                st.markdown(f"**Framework:** {self.get_framework_icon(metadata['framework'])} {metadata['framework']}")
                st.markdown(f"**Difficulty:** {self.get_difficulty_color(metadata['difficulty'])} {metadata['difficulty']}")
                
                if metadata.get('user_generated', False):
                    st.markdown("**Type:** 👤 User-generated")
                else:
                    st.markdown("**Type:** 🏭 Built-in")
            
            # Show code in a collapsible section
            with st.expander("📄 View Source Code", expanded=False):
                code = self.get_example_code(filename)
                if code:
                    st.code(code, language="python")
                else:
                    st.error(f"Could not load source code for {filename}")
    
    def filter_examples(self, framework_filter: str, difficulty_filter: str, search_term: str, source_filter: str = "All") -> Dict:
        """Filter examples based on criteria"""
        filtered = {}
        
        for filename, metadata in self.examples_metadata.items():
            # Framework filter
            if framework_filter != "All" and metadata.get('framework', '') != framework_filter:
                continue
            
            # Difficulty filter
            if difficulty_filter != "All" and metadata.get('difficulty', '') != difficulty_filter:
                continue
            
            # Source filter
            if source_filter == "Built-in" and metadata.get('user_generated', False):
                continue
            elif source_filter == "User-generated" and not metadata.get('user_generated', False):
                continue
            
            # Search filter
            if search_term:
                search_text = f"{metadata.get('title', '')} {metadata.get('description', '')} {' '.join(metadata.get('features', []))}"
                if search_term.lower() not in search_text.lower():
                    continue
            
            filtered[filename] = metadata
        
        return filtered


def display_examples_section() -> tuple:
    """Main function to display examples section"""
    library = ExamplesLibrary()
    return library.display_examples_library()


def add_to_examples_gallery(query: str, config_ideas: str, generation_plan: str, 
                           generated_code: str, framework_choice: str,
                           custom_title: str = None, custom_description: str = None,
                           custom_difficulty: str = "Intermediate") -> tuple:
    """Add a new example to the gallery - local function"""
    from ui.examples_library import ExamplesLibrary
    
    library = ExamplesLibrary()
    return library.add_example_to_gallery(
        query, config_ideas, generation_plan, generated_code, framework_choice,
        custom_title, custom_description, custom_difficulty
    )

                                         