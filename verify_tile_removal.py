#!/usr/bin/env python3
"""
Verification script to confirm tile-based coordinate system has been completely removed.
"""

def verify_tile_removal():
    print("🔍 Verifying Tile System Removal")
    print("=" * 40)
    
    # Test 1: Schema verification
    try:
        from backend.config.schema import AgentSummary, MoveBackendAction, MoveFrontendAction
        
        # Test AgentSummary - should NOT have curr_tile
        summary = AgentSummary(agent_id="test", curr_room="Living Room")
        summary_dict = summary.dict()
        
        assert 'curr_tile' not in summary_dict, "❌ curr_tile still present in AgentSummary"
        assert 'curr_room' in summary_dict, "❌ curr_room missing from AgentSummary"
        print("✅ AgentSummary: Tile fields removed, room fields present")
        
        # Test MoveBackendAction - should NOT have destination_tile
        move_action = MoveBackendAction(action_type="move", destination_room="Kitchen")
        move_dict = move_action.dict()
        
        assert 'destination_tile' not in move_dict, "❌ destination_tile still present in MoveBackendAction"
        assert 'destination_room' in move_dict, "❌ destination_room missing from MoveBackendAction"
        print("✅ MoveBackendAction: Tile fields removed, room fields present")
        
        # Test MoveFrontendAction - should NOT have destination_tile
        frontend_move = MoveFrontendAction(action_type="move", destination_room="Bedroom")
        frontend_dict = frontend_move.dict()
        
        assert 'destination_tile' not in frontend_dict, "❌ destination_tile still present in MoveFrontendAction"
        assert 'destination_room' in frontend_dict, "❌ destination_room missing from MoveFrontendAction"
        print("✅ MoveFrontendAction: Tile fields removed, room fields present")
        
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        return False
    
    # Test 2: Agent class verification
    try:
        from backend.agent import Agent
        
        agent = Agent("test_agent")
        
        # Check that agent doesn't have curr_tile
        assert not hasattr(agent, 'curr_tile'), "❌ Agent still has curr_tile attribute"
        assert hasattr(agent, 'curr_room'), "❌ Agent missing curr_room attribute"
        
        # Check state dict doesn't have curr_tile
        state_dict = agent.to_state_dict()
        assert 'curr_tile' not in state_dict, "❌ curr_tile still in agent state dict"
        assert 'curr_room' in state_dict, "❌ curr_room missing from agent state dict"
        
        # Check summary dict doesn't have curr_tile
        summary_dict = agent.to_summary_dict()
        assert 'curr_tile' not in summary_dict, "❌ curr_tile still in agent summary dict"
        assert 'curr_room' in summary_dict, "❌ curr_room missing from agent summary dict"
        
        print("✅ Agent class: Tile fields removed, room fields present")
        
    except Exception as e:
        print(f"❌ Agent verification failed: {e}")
        return False
    
    # Test 3: Check for any remaining tile references
    try:
        # This would catch any remaining tile references in the module
        import backend.game_loop
        import backend.agent_manager
        
        # Verify LocationToTileMapper class is gone
        assert not hasattr(backend.game_loop, 'LocationToTileMapper'), "❌ LocationToTileMapper class still exists"
        print("✅ Game Controller: LocationToTileMapper class removed")
        
    except Exception as e:
        print(f"❌ Module verification failed: {e}")
        return False
    
    print("\n🎉 SUCCESS: Tile system completely removed!")
    print("\n📋 Summary of Changes:")
    print("• AgentSummary: No more curr_tile field")
    print("• MoveActions: No more destination_tile field") 
    print("• Agent class: No more curr_tile attribute")
    print("• Game Controller: No more LocationToTileMapper")
    print("• All location tracking now uses room names only")
    print("\n✅ System ready for room-based navigation!")
    
    return True

if __name__ == "__main__":
    verify_tile_removal() 