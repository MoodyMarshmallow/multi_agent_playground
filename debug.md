# Debug Findings: "get apple" Command Issue

## Problem Summary
The "get apple" command appears in action discovery but fails validation in agent tests. The agent can see the apple but "get apple" is missing from available commands during execution.

## Key Findings

###  What's Working
1. **Action Discovery Logic**: Pattern-based discovery works perfectly
   - Get action has `COMMAND_PATTERNS: ['get {item}']` 
   - Apple is discovered with `get_applicable_combinations: [{'item': 'apple'}]`
   - Preconditions pass: `check_preconditions() = True`

2. **Core Game Engine**: Basic functionality is correct
   - Apple exists in Kitchen with `gettable=True`
   - Item matching works: `match_item("get apple")` finds apple
   - Multiple calls to `get_available_actions()` are consistent

3. **Debug Script Results**: Everything works in isolation
   - `debug_actions.py` shows "get apple" in available actions
   - All precondition tests pass
   - Multiple characters don't interfere with discovery

### L What's Failing
1. **Agent Test Environment**: Test execution shows inconsistency
   - Navigation test: Apple appears correctly with "get apple" action
   - Collection test: "get apple" missing from available actions list
   - Agent sees apple in world state but can't access get command

2. **Test Output Evidence**:
   ```
   Available actions:
     - examine apple: Examine an item  ê Present
     - get apple: Pick up the apple    ê Missing in validation
   ```

### = Root Cause Analysis
The issue is **NOT** in:
- Pattern-based action discovery system (works perfectly)
- Get action preconditions (all pass)
- Item setup or properties (apple has gettable=True)
- Core parsing logic (consistent in debug tests)

The issue **IS** in:
- **Agent testing framework execution environment**
- Difference between how `get_world_state_for_agent()` is called in tests vs debug
- Possible character setup differences between test environment and debug script

### =‡ Current Investigation Status
1. **Completed**: Verified core action discovery system works
2. **Completed**: Confirmed preconditions pass in isolation
3. **Completed**: Ruled out Unicode/emoji encoding issues
4. **In Progress**: Identified test framework environment differences
5. **Next**: Need to investigate test character setup vs debug script setup

### =À Key Debug Commands
```bash
# Test action discovery in isolation
python debug_actions.py

# Run agent tests with debug logging
python run_agent_tests.py --debug

# Check specific action availability
python -c "
from debug_actions import *
available = game.parser.get_available_actions(game.player)
print([a['command'] for a in available if 'apple' in a['command']])
"
```

### =' Potential Solutions to Investigate
1. **Character Setup Differences**: Compare test agent creation vs debug script
2. **Game State Timing**: Check if actions are called at different game states
3. **World State Generation**: Verify `get_world_state_for_agent()` behavior in tests
4. **Action Discovery Context**: Ensure same parser/game instance is used

### =› Files Modified
- `backend/text_adventure_games/parsing.py`: Added logging, removed old action system
- `backend/testing/agent_test_runner.py`: Added `gettable=True` to test items  
- `run_agent_tests.py`: Added logging configuration and .env loading
- `debug_actions.py`: Comprehensive testing script

### <Ø Next Steps for New Claude Instance
1. Focus on test framework character setup differences
2. Compare exact game state between test environment and debug script
3. Investigate why `get_world_state_for_agent()` returns different actions in tests
4. Trace the exact execution path in agent testing framework