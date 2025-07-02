#!/usr/bin/env python3
"""
Quick test to verify the backend works after removing tiles.
"""

try:
    print("Testing imports...")
    
    # Test schema imports
    from backend.config.schema import AgentSummary, MoveBackendAction
    print("✓ Schema imports successful")
    
    # Test agent summary without tiles
    summary = AgentSummary(agent_id="test", curr_room="Living Room")
    print(f"✓ AgentSummary created: {summary}")
    
    # Test move action without tiles
    move_action = MoveBackendAction(action_type="move", destination_room="Kitchen")
    print(f"✓ MoveBackendAction created: {move_action}")
    
    print("✅ All tests passed! Tile system successfully removed.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 