#!/usr/bin/env python3
"""
Manual Debug Mode Runner
========================
Run the multi-agent playground with manual control for debugging and testing.
Allows developers to manually control agents instead of using AI.

Usage Examples:
--------------
# Run with all agents manual (default)
python run_manual_debug.py

# Make alex_001 automatic (AI), alan_002 stays manual
python run_manual_debug.py --ai alex_001

# Make both agents automatic (AI)
python run_manual_debug.py --ai alex_001 alan_002

# Make all agents automatic (shortcut)
python run_manual_debug.py --all-ai

# Run for 100 turns with alex automatic
python run_manual_debug.py --ai alex_001 --turns 100

# Mixed configuration with custom turn limit
python run_manual_debug.py --ai alan_002 --turns 25

Programmatic Usage:
------------------
# You can also use GameLoop directly in your code:
from backend.game_loop import GameLoop

# Create agent configuration
agent_config = {"alex_001": "manual", "alan_002": "ai"}
game_loop = GameLoop(agent_config=agent_config)
await game_loop.start()
"""

import asyncio
import argparse
import sys
from typing import Dict

from backend.game_loop import GameLoop


async def main():
    """Main entry point for manual debug mode."""
    parser = argparse.ArgumentParser(description="Run multi-agent playground with manual agent control (default: all manual)")
    parser.add_argument("--ai", nargs="*", default=[], 
                       help="Agent names to control with AI (e.g., alex_001 alan_002)")
    parser.add_argument("--all-ai", action="store_true", 
                       help="Make all agents AI")
    parser.add_argument("--turns", type=int, default=50, 
                       help="Maximum number of turns to run (default: 50)")
    
    args = parser.parse_args()
    
    # Build agent configuration - default to all manual
    agent_config: Dict[str, str] = {}
    
    if args.all_ai:
        # Make all agents AI
        agent_config = {"alex_001": "ai", "alan_002": "ai"}
    elif args.ai:
        # Make specified agents AI, others manual
        for agent_name in ["alex_001", "alan_002"]:
            agent_config[agent_name] = "ai" if agent_name in args.ai else "manual"
    else:
        # Default: all agents manual
        agent_config = {"alex_001": "manual", "alan_002": "manual"}
    
    # Display configuration
    print("Multi-Agent Playground - Manual Debug Mode")
    print("=" * 50)
    
    manual_agents = [name for name, type_ in agent_config.items() if type_ == "manual"]
    ai_agents = [name for name, type_ in agent_config.items() if type_ == "ai"]
    print(f"Manual agents: {manual_agents}")
    print(f"AI agents: {ai_agents}")
    
    if not ai_agents:
        print("Use --ai <agent_name> or --all-ai to make agents automatic.")
    
    print(f"Max turns: {args.turns}")
    print("\nPress Ctrl+C to stop the game at any time.")
    print("=" * 60)
    print()
    
    # Create and start the game loop with agent configuration
    game_loop = GameLoop(agent_config=agent_config)
    game_loop.max_turns_per_session = args.turns
    
    try:
        await game_loop.start()
        
        # Wait for the game to finish or be interrupted
        while game_loop.is_running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await game_loop.stop()
        print("Game stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)