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

Work in progress.

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


python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt


