# 🤖 AI Simulator

A powerful AI-driven platform for creating, learning, and experimenting with physics simulations using PyGame and Ursina. Generate interactive simulations with just natural language descriptions and explore the physics behind them!

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![PyGame](https://img.shields.io/badge/PyGame-2.5+-green.svg)

## 🌟 Features

### 🎮 **Multi-Framework Support**
- **PyGame Simulations**: 2D physics simulations with interactive controls
- **Ursina Engine**: 3D simulations and visualizations
- **Extensible Architecture**: Easy to add new frameworks

### 🤖 **AI-Powered Generation**
- **Natural Language Input**: Describe simulations in plain English
- **Multi-Modal Input**: Text, file upload, or audio recording
- **Intelligent Agents**: Specialized AI agents for configuration, planning, and code generation
- **Physics-Aware**: Generates scientifically accurate simulations with proper formulas

### 🔧 **Multiple AI Providers**
- **OpenAI**: GPT-4o, GPT-5, GPT-4o Mini
- **Anthropic**: Claude 3.5 Sonnet, Claude 4, Claude Opus 4.1
- **Google**: Gemini 2.0 Flash, Gemini 2.5 Pro, Gemini 1.5 Pro
- **DeepSeek**: DeepSeek R1, DeepSeek V3, DeepSeek Coder V2
- **Mistral**: Mistral Large 2, Codestral, Mistral Medium 3.1
- **Cerebras**: GPT OSS 120B, Llama 4 Maverick, Llama 4 Scout
- **Grok**: DeepSeek R1 Distill, Kimi K2 Instruct
- **OpenRouter**: Access to 15+ models including Qwen 3 series

### 🎓 **Educational Features**
- **Code Explanation**: AI-powered code explanations
- **Learning Materials**: Physics concepts, formulas, and theories
- **Interactive Examples**: Pre-built physics demonstrations
- **Real-time Experimentation**: Modify parameters and see immediate results

### 💻 **Development Tools**
- **Live Code Editor**: Syntax highlighting with Monaco/ACE editor
- **Python Playground**: Run and test code in real-time
- **Chat Interface**: Iterative improvements with conversation context
- **Project Management**: Save, load, and export complete projects

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-simulator.git
   cd ai-simulator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys** (choose at least one provider)
   ```bash
   # OpenAI
   export OPENAI_API_KEY="your_openai_api_key"
   
   # Anthropic
   export ANTHROPIC_API_KEY="your_anthropic_api_key"
   
   # Google Gemini
   export GEMINI_API_KEY="your_gemini_api_key"
   
   # DeepSeek
   export DEEPSEEK_API_KEY="your_deepseek_api_key"
   
   # Mistral
   export MISTRAL_API_KEY="your_mistral_api_key"
   
   # Other providers (optional)
   export CEREBRAS_API_KEY="your_cerebras_api_key"
   export GROK_API_KEY="your_grok_api_key"
   export OPENROUTER_API_KEY="your_openrouter_api_key"
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 🎯 Usage Examples

### Creating a Bouncing Ball Simulation
1. Select your AI provider and model
2. Enter: "Create a bouncing ball simulation with gravity and adjustable elasticity"
3. Click "Generate PyGame Code"
4. Use the playground to run and modify the simulation

### Loading Example Simulations
- Visit the **Examples Library** tab
- Choose from pre-built simulations:
  - 🏀 Bouncing Balls Physics
  - 🎱 Billiard Ball Dynamics
  - 📦 Newton's 3rd Law Demo
  - 🚀 Projectile Motion
  - ⚖️ Pendulum Simulation

### Using Audio Input
1. Click the microphone icon
2. Record your simulation description
3. The AI will transcribe and generate code automatically

## 🏗️ Project Structure

```
ai-simulator/
├── app.py                    # Main Streamlit application
├── prompts.py               # AI prompt templates
├── requirements.txt         # Python dependencies
├── agents/                  # AI agent modules
│   ├── base_agent.py       # Base agent class
│   ├── configurator_agent.py # Configuration suggestions
│   ├── planner_agent.py    # Implementation planning
│   ├── code_gen_agent.py   # Code generation
│   └── learning_agent.py   # Educational content
├── config/                  # Configuration files
│   ├── models_config.py    # AI model configurations
├── ui/                      # User interface components
│   ├── main_ui.py          # Main UI logic
│   ├── model_selector.py   # Model selection interface
│   ├── examples_library.py # Examples management
│   └── examples_metadata.json # Example descriptions
├── utils/                   # Utility functions
│   ├── transcription.py    # Audio transcription
│   └── python_runner.py    # Code execution
├── examples/                # Pre-built simulations
│   ├── balls_dropping.py
│   ├── billiard_balls.py
│   ├── collision_box_wall.py
│   ├── newtons3rd_law.py
│   └── projectile_motion.py
    └── motion_of_pendulum.py
```

## 🧠 AI Agent Architecture

### **Configurator Agent**
- Analyzes user requirements
- Suggests interactive features and parameters
- Focuses on educational value and engagement

### **Planner Agent**
- Creates detailed implementation plans
- Structures the development approach
- Ensures comprehensive feature coverage

### **Code Generation Agent**
- Generates complete, runnable simulations
- Implements physics-accurate calculations
- Creates interactive user interfaces

### **Learning Agent**
- Generates educational explanations
- Provides physics concepts and formulas
- Creates learning objectives and extensions

## 🔧 Configuration

### Adding New AI Providers
Edit `config/models_config.py`:
```python
MODEL_PROVIDERS["NewProvider"] = {
    "api_key_env": "NEW_PROVIDER_API_KEY",
    "base_url": "https://api.newprovider.com/v1",
    "models": {
        "new-model": {
            "name": "New Model",
            "description": "Description of the model",
            "max_tokens": 4096,
            "cost": "Medium"
        }
    }
}
```

### Customizing Prompts
Modify `prompts.py` to adjust AI behavior:
- `get_configurator_prompt()`: Configuration suggestions
- `get_planner_prompt()`: Implementation planning
- `get_code_gen_prompt()`: Code generation
- `get_learning_prompt()`: Educational content

## 📚 Example Simulations

### 🏀 **Bouncing Balls**
- Interactive elasticity controls
- Gravity adjustment
- Ball-to-ball collisions
- Ground angle modification

### 🎱 **Billiard Physics**
- Realistic ball dynamics
- Momentum conservation
- Force application
- Collision highlighting

### 📦 **Newton's Laws Demo**
- Force vector visualization
- Interactive mass and velocity
- Friction effects
- Energy calculations

### 🚀 **Projectile Motion**
- Adjustable launch parameters
- Wind resistance effects
- Trajectory prediction
- Target practice mode

## 🎓 Educational Features

### **Physics Learning**
- Real-time formula display
- Mathematical derivations
- Physics principle explanations
- Units and dimensional analysis

### **Code Learning**
- Step-by-step code explanations
- Programming concept tutorials
- Best practices demonstrations
- Algorithm explanations

### **Interactive Experiments**
- Parameter exploration
- Hypothesis testing
- Comparative analysis
- Scientific method application


### Adding New Examples
1. Create your simulation file in `examples/`
2. Add metadata to `ui/examples_metadata.json`
3. Test the example in the Examples Library

<!-- ## 📊 Supported Physics Concepts

- **Mechanics**: Kinematics, dynamics, collisions
- **Energy**: Kinetic, potential, conservation
- **Forces**: Gravity, friction, air resistance
- **Waves**: Oscillations, pendulums, springs
- **Thermodynamics**: Heat transfer, gas laws
- **Electromagnetism**: Electric fields, magnetic forces -->

<!-- ## 🚀 Future Roadmap

- [ ] 3D Physics with Ursina Engine
- [ ] VR/AR Simulation Support
- [ ] Collaborative Multi-user Sessions
- [ ] Advanced Physics (Quantum, Relativity)
- [ ] Machine Learning Integration
- [ ] Mobile App Development
- [ ] Cloud Deployment Options
- [ ] Educational Curriculum Integration

---

**Made with ❤️ for physics education and AI-powered learning**

⭐ **Star this repo** if you find it helpful! -->