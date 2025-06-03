# Copy and paste your OpenAI API Key
openai_api_key = "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"
# Put your name
key_owner = "Multi-Agent Playground"

import os

# Get the absolute path to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

maze_assets_loc = os.path.join(project_root, "frontend", "frontend_server", "static_dirs", "assets")
env_matrix = os.path.join(maze_assets_loc, "the_ville", "matrix")
env_visuals = os.path.join(maze_assets_loc, "the_ville", "visuals")

fs_storage = os.path.join(project_root, "frontent", "frontend_server", "storage")
fs_temp_storage = os.path.join(project_root, "frontend", "frontend_server", "temp_storage")

collision_block_id = "32125"

# Verbose 
debug = True