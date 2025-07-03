# multi_agent_playground
# 🧠 Multi-Agent Playground

A simplified multi-agent simulation framework inspired by [joonspk-research/generative_agents](https://github.com/joonspk-research/generative_agents), 
with an added **Godot frontend** for real-time simulation and interaction.

## 🔧 Project Structure
- \`backend/\`: Core simulation logic (agent identity, planning, actions)
- \`frontend/godot/\`: Godot engine UI and world rendering
- \`data/\`: JSON definitions of agents and the environment
- \`docs/\`: Notes, schemas, and protocol definitions
- \`tests/\`: Python unit tests

🛠️ Note: This project is currently under active development.

---

Currently, the project uses: but feel free to modify 

fastapi – A fast, modern Python web framework for building backend APIs. Used to serve agent states and interact with the frontend (Godot).

uvicorn – A lightweight ASGI server that runs your FastAPI app.

---
## ⚙️ Setup Instructions

### ✅ 1. Clone the Repository

```bash
git clone link
cd multi-agent-playground
```

### ✅ 2. Set up the virtual environment and activate
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### ✅ 3. # Start the FastAPI server at the backend
```bash
python -m uvicorn backend.main:app --reload
```

### ✅ 4. Set up the frontend and commands to run the frontend
Install Godot (version 3.5 or later recommended).

In Godot, open the project file located at:
frontend/Godot-Multi-Agent-Playground/project.godot

Navigate to the following scene file:
frontend/Godot-Multi-Agent-Playground/scenes/characters/navigation_player/navigation_player.gd

Click the ▶️ "Run Current Scene" button in the top-right corner or ctrl/command + R.

Arrow keys – Move the agent

Right-click – Move agent to selected position

R key – Request the next planned action from the backend

