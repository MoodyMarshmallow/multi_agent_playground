 High-level verdict

  • Overall: The refactor substantially improves separation of concerns and aligns     
    well with the proposed layered architecture and Kani best practices.
  • Big wins: Clean domain layer, async event bus, configuration-driven
    agents/worlds, orchestration layer bridging domain and infra, proper Kani
    function-calling pattern.
  • Notable gaps: Initial world state isn’t injected into Kani agents at init;
    agent_id vs character_name mapping is brittle; duplicate AgentStrategy protocols;  
    minor layering leaks; Windows-specific SSL hack inside agent.


  What’s done well (matches DESIGN.md and Kani docs)

  • Layering and boundaries
    • Domain layer (backend/domain/**) is pure: entities, services (SimulationEngine,  
       TurnScheduler), and event interfaces are infra-free.
    • Application service GameOrchestrator coordinates domain services with infra      
      (AgentManager, Game, EventBus) as intended.
    • Infra implements EventBus as AsyncEventBus and LLM engines via EngineFactory;    
      HTTP endpoints live under interfaces/http.
  • Event bus integration
    • EventBus interface and AsyncEventBus implement publish/subscribe,
      unserved-event polling, and background processing. HTTP endpoints and GameLoop   
      consume via the bus instead of a list.
  • Kani integration
    • KaniAgent extends Kani directly, defines @ai_function submit_command(command:    
      str), and uses full_round(..., max_function_rounds=1).
    • Action selection uses prior turn’s result; recent-actions memory to reduce       
      loops; look fallback is safe.
    • Engine abstraction set up with EngineFactory and Pydantic configs for
      OpenAI/Anthropic in config/agents.yaml.
  • External configuration
    • Agents are defined in config/agents.yaml using AgentConfig/ModelConfig;
      validated with Pydantic.
    • Worlds are defined in config/worlds/*.yaml and built with WorldBuilder.
  • Backwards compatibility
    • GameLoop now delegates to GameOrchestrator, preserving public API and HTTP       
      contracts.


  Issues and risks to address

  • Initial world state not injected to Kani agents (design gap)
    • Design doc and repo rules specify: on agent creation, run a look and pass        
      formatted world state as the first user message.
    • GameOrchestrator has _get_initial_world_state_for_agent(...) but doesn’t use it  
       to set KaniAgent.initial_world_state.
    • AgentStrategyLoader constructs KaniAgent with initial_world_state=None, and no   
      later step populates it. Agents must “guess” to look, which deviates from the    
      intended first-turn UX.
  • Agent identity mapping is brittle
    • AgentManager.register_agent_strategy API expects a character_name but
      GameOrchestrator calls it with agent_id. This only works because agent_id ==     
      character_name in current YAML.
    • AgentManager.previous_action_results is keyed by character name internally,      
      while GameOrchestrator.execute_next_turn fetches previous results by agent_id.   
      The AgentExecutor re-writes the correct key later, but this inconsistency will   
      break if character names differ from agent IDs.
  • Duplicate `AgentStrategy` protocol definitions
    • There are two definitions: backend/domain/entities/agent_strategy.py and
      another in backend/infrastructure/agents/kani_agent.py.
    • This can confuse typings and violates single source of truth; infra and app      
      should depend on the domain protocol.
  • Application layer importing infra agents
    • AgentStrategyLoader (application) imports KaniAgent/ManualAgent from infra.      
      It’s acceptable as a factory/adapter, but by-the-book Clean Architecture would   
      push these constructions to an infra factory injected into application.
  • Windows SSL hack inside `KaniAgent`
    • Hard-coded Windows paths in KaniAgent.__init__() bake environment specifics      
      into the agent. This should move to engine setup (infra) or environment
      bootstrap, not the agent logic.
  • Event persistence
    • Bus is in-memory only (as planned). Fine for Phase 3, but highlight that
      durability/horizontal scaling is pending.


  Fit to Kani best practices

  • Good
    • Direct subclass of Kani with @ai_function, one function-call round, side-effect  
       capture of chosen action.
    • Clear system prompt and single-action enforcement guidance.
  • To tighten
    • Ensure initial world state is actually passed once as the first user message to  
       match the documented prompting strategy.
    • Consider centralizing prompt fragments to avoid duplication between
      EnhancedLookAction._format_world_state and KaniAgent._format_world_state
      (they’re already very similar; keeping a single formatter prevents drift).       


  Prioritized recommendations

  • P1: Inject initial world state at agent setup
    • After world build and agent registration, for each KaniAgent, compute initial    
      state with EnhancedLookAction and assign agent.initial_world_state so first      
      select_action gets the full context.
  • P1: Standardize ID vs name usage
    • Pick a single key for AgentManager.agent_strategies and previous_action_results  
       (recommend agent_id everywhere). Translate to character_name only when
      touching the game API. This removes hidden coupling to YAML equality.
  • P2: Remove protocol duplication
    • Delete the infra-local AgentStrategy and have all layers import the domain       
      AgentStrategy protocol.
  • P2: Move SSL/env hacks out of `KaniAgent`
    • Relocate to engine creation/bootstrap so agents stay behavior-only.
  • P3: Minor layering cleanup
    • Optionally extract infra-specific construction from AgentStrategyLoader into an  
       injected infra factory to fully respect dependency boundaries.
  • Optional: Deduplicate world-state formatting in one utility to keep agent and      
    look output aligned.
  • Optional: Add a simple smoke test that runs one turn and verifies that:
    • First turn receives initial world state (no prior action result)
    • look does not end turn; other actions do
    • /agent_act/next returns unserved events once
  • Optional: Add provider “custom” plumbing in EngineFactory or remove from
    ModelConfig if not supported yet.
  • Optional: Document that /agents/states expects repeated agent_ids query params.    
  • Optional: In AsyncEventBus.clear_events(event_type=...), the served-tracking reset 
     is coarse. Consider pruning only affected IDs if you later depend on served       
    counts.
  • Optional: Consider shorter loop delay or adaptive scheduling in
    GameLoop.run_game_loop for responsiveness.
  • Optional: Ensure GameEventList construction remains consistent if event schema     
    evolves; currently it converts AgentActionOutput fine.
  • Optional: Make AgentManager.execute_agent_turn guard against missing
    schema_exporter or parser errors more explicitly.
  • Optional: Ensure requirements.txt includes correct kani[openai]/kani[anthropic]    
    extras as the design assumes.
  • Optional: CI test for config validation using
    AgentStrategyLoader.validate_configuration.
  • Optional: Confirm Anthropic engine import path (kani.engines.anthropic) matches    
    installed Kani version.
  • Optional: Unify YAML character definitions and agent definitions: if they
    diverge, ensure orchestrator aligns them or fails fast with a clear error.
  • Optional: Consider backpressure on event queue if frontend poller stalls.
  • Optional: Add a single place for constants like event types instead of string      
    duplication.
  • Optional: Clarify the contract for turn continuation: the scheduler only advances  
    on ends_turn=True; ensure all actions correctly set ends_turn.
  • Optional: Consider multi-agent parallel turns later; current design makes that     
    feasible via domain abstractions.
  • Optional: Remove legacy helper methods in GameLoop if not used (after ensuring     
    test coverage).
  • Optional: Add structured logging of action_schema to aid debugging.
  • Optional: Validate that chat actions’ ends_turn semantics are correct per design.  
  • Optional: Keep engine cache keys deterministic to avoid creating multiple engines  
    per agent restart if that's desired.
  • Optional: Add metrics/tracing hooks in GameOrchestratorEventPublisher as planned   
    future work.
  • Optional: Ensure WSL/Windows path handling for config files stays robust; current  
    absolute-path normalization looks fine.
  • Optional: In get_game_events, generating id=hash(event.timestamp) can collide;     
    consider monotonic IDs or event UUID conversion if needed.
  • Optional: Guarantee that AgentActionEvent.agent_id is set consistently to
    agent_id (not character_name) for downstream consumers.
  • Optional: Return meaningful HTTP error on get_agents/states for unknown IDs        
    rather than skip, if that’s preferred by the frontend.
  • Optional: Add test that verifies look shows chat affordances (pending requests)    
    since you surface that in agent feedback.
  • Optional: Add stricter typing to engine factory return types if practical.
  • Optional: Consider moving objects registry into domain/application if it becomes   
    part of core state, but current infra placement is fine.
  • Optional: Align YAML world characters and agents.yaml to ensure names and initial  
    locations stay in sync; enforce in validation.
  • Optional: Gate verbose logs via env to avoid noisy production logs.
  • Optional: If using uv for commands (per CLAUDE.md), ensure docs/scripts call uv    
    consistently; not a code issue but a dev-experience one.
  • Optional: Add retry/backoff to publish if you later swap in a broker.
  • Optional: Keep EnhancedLookAction and agent’s state formatter perfectly in sync    
    by calling a shared formatter.
  • Optional: Ensure Kani version supports the used API; pin in requirements.txt.      
  • Optional: Consider seeding conversation with a “Recent actions” system message     
    instead of appending to observation; current approach works though.
  • Optional: Refine the prompt’s “Only choose from available actions” if the game     
    does not strictly enforce it; maybe rephrase as “Prefer available actions”.        
  • Optional: Document manual agent’s temporary behavior prominently since it always   
    returns look.
  • Optional: Validate the ends_turn behavior for chat requests and responses matches  
    UX intent.
  • Optional: In GameOrchestrator.reset, confirm event bus lifecycle order is okay     
    (stop then re-init).
  • Optional: Add a health endpoint for orchestrator init status.
  • Optional: Surface turn stats via /game/status more richly if frontend needs.       
  • Optional: Ensure Pydantic v1/v2 usage is consistent; you already guard action      
    field extraction both ways.
  • Optional: Ensure GameEventList serialization stays stable across schema changes.   
  • Optional: Use asyncio.create_task safely with proper exception handling (already   
    okay).
  • Optional: Consider switching GameLoop to drive from ticks or events rather than    
    fixed sleeps if you need responsiveness.
  • Optional: If large numbers of events accumulate, provide paging/limits.
  • Optional: Verify concurrency safety of shared dicts if you move to concurrent      
    execution later.
  • Optional: Add plugin mechanism scaffolding for 3rd-party strategies if needed      
    beyond “custom class”.
  • Optional: Align naming: “orchestrator” vs “controller” across code/docs for        
    clarity.
  • Optional: Ensure world config validation fails fast when characters and agents     
    mismatch.
  • Optional: Move string literals like “frontend” consumer ID to a const.
  • Optional: Provide a way to inject engines for testing (mock engines);
    EngineFactory can be swapped with a test double.
  • Optional: Stabilize the API of AgentManager to use domain Agent or IDs rather      
    than Character to reduce coupling to game engine.
  • Optional: Consider trimming duplicate imports and docstrings for brevity.
  • Optional: Add lint/type checks in CI.
  • Optional: Expose a dry-run validation CLI via uv.
  • Optional: Keep manual control agent opt-in only to avoid surprises in production.  
  • Optional: Add informative errors when YAML world references missing locations or   
    items.
  • Optional: Provide a migration note in README for refactor changes.
  • Optional: Ensure /agents/states is used or remove to avoid bitrot.
  • Optional: Confirm schema object house_action union and downstream consumers still  
    align.
  • Optional: Consider freezing dataclasses where sensible.
  • Optional: Reconcile GameLoop’s output logging with event bus to prevent
    duplicate/conflicting logs.
  • Optional: Test event ordering from _event_queue when multiple actions publish in   
    quick succession.
  • Optional: Provide hooks to throttle Kani calls in load testing.
  • Optional: Provide agent-level timeouts and error handling policy in
    SimulationEngine or executor.
  • Optional: Align exception types between layers for clarity.
  • Optional: Add comprehensive docstrings for public APIs.
  • Optional: Provide structured error responses in HTTP endpoints.
  • Optional: Tighten type hints for public functions returning dicts to explicit      
    models.
  • Optional: Consider memory bounds for AsyncEventBus storage.
  • Optional: Consistent naming for schemas: AgentActionOutput vs domain events.       
  • Optional: Add utility to safely downcast Pydantic v1/v2 differences.
  • Optional: Confirm Godot frontend expects the new /agent_act/next semantics.        
  • Optional: Measure and tune turn latency.
  • Optional: Reuse a single engine per agent by cache key; you already support that.  
  • Optional: Note Anthropic model names may differ; keep configurable.
  • Optional: Secure config file paths; current approach is fine for dev.
  • Optional: Provide deterministic test world to reduce flakiness.
  • Optional: Consider trace IDs to tie turns to events.
  • Optional: Validate openable container state transitions.
  • Optional: Add playback/replay facility based on domain events later.
  • Optional: Ensure GameOrchestratorEventPublisher doesn’t leak tasks on reset.       
  • Optional: Clarify how “noop” actions are surfaced to frontend.
  • Optional: Provide a developer-mode endpoint to inspect turn history.
  • Optional: Check for Python version compatibility in CI.
  • Optional: Do a pass to standardize logging format across layers.
  • Optional: Provide minimal docs for adding a new LLM provider.
  • Optional: Address duplicated _format_world_state to prevent drift.
  • Optional: Ensure license headers are consistent post-refactor.
  • Optional: Run through tests to ensure coverage of the new flows.
  • Optional: Keep an eye on doc references that still mention the old structure.      
  • Optional: If you plan horizontal scale, consider making event bus pluggable        
    (e.g., Redis, Kafka) with same interface.
  • Optional: Ensure cancellation handling in long-running loops is robust.
  • Optional: Provide explicit backpressure in event publisher if future bus is        
    remote.
  • Optional: Think about idempotency of events if retries are added.
  • Optional: Provide config to disable specific agents for tests.
  • Optional: Verify that agents cannot “overrun” turn by calling multiple actions;    
    current single max_function_rounds=1 helps.
  • Optional: Consider embedding available actions list directly in observations; you  
    already do for look.
  • Optional: Keep function names consistent: select_action across all strategies.     
  • Optional: Ensure Kani’s engine kwargs match the installed version; pin.
  • Optional: Build a tiny Kani mock for tests.
  • Optional: Cleanup leftover TODOs in ManualAgent.
  • Optional: Guard against huge recent_actions lists.
  • Optional: Validate that Game.schema_exporter.get_schema() is always available at   
    that point.
  • Optional: Confirm that AgentActionEvent.from_agent_action_output maps fields       
    expected by the Godot frontend.
  • Optional: Decide whether /game/events is retained if /agent_act/next suffices.     
  • Optional: Consider move to typed responses for get_world_state.
  • Optional: Use dependency injection more broadly to ease testing.
  • Optional: Unify character/persona sources between YAMLs.
  • Optional: Provide safe handling for agents without strategies (currently ends      
    turn; OK).
  • Optional: Allow pausing per agent for debugging.
  • Optional: Ensure no blocking IO in async paths (loading YAML is done at init;      
    OK).
  • Optional: Consider separate loop or tick for simulation vs HTTP.
  • Optional: Document that ends_turn=False for look is by design.
  • Optional: Add pre-flight check for API keys on startup.
  • Optional: Be cautious about changing AgentActionOutput schema; it’s the API        
    contract.
  • Optional: Add test ensuring that events are delivered once to frontend.
  • Optional: Check for race conditions on event bus if you later enable parallel      
    agent execution.
  • Optional: Confirm memory safety of event store with prolonged runs.
  • Optional: Provide metrics for publish/subscribe times.
  • Optional: Dump config validation errors clearly.
  • Optional: Provide versioning in config files.
  • Optional: Document base class responsibilities vs strategy responsibilities.       
  • Optional: Provide a small diagram mapping layers (already in DESIGN.md
    implicitly).
  • Optional: Validate that chat actions have correct ends_turn semantics per your     
    docs.
  • Optional: Make ActionEventPublisher.add_event_handler removal explicit if fully    
    replaced by bus.
  • Optional: Review error messages for clarity to users.
  • Optional: Add smoke test that spins FastAPI + single step to ensure end-to-end     
    works.
  • Optional: Ensure project scripts use uv consistently (per your rules).
  • Optional: Consider caching schema exporter outputs if heavy.
  • Optional: Ensure item property application covers all supported properties.        
  • Optional: Use strict mypy in domain/application.
  • Optional: Warn if agents.yaml contains unknown provider.
  • Optional: Add config for per-agent temps.
  • Optional: Use structured result for execute_next_turn if you grow more metadata.   
  • Optional: De-duplicate logger names and log structure.
  • Optional: Provide quickstart section for the new architecture.
  • Optional: Consider default to look on first turn if initial state missing.
  • Optional: Make consistent the house_action naming across code.
  • Optional: Add health checks for event bus running.
  • Optional: Document required env vars in README.
  • Optional: Pin dependency versions to ensure reproducibility.
  • Optional: Nice-to-have: plugin discovery via entry points.
  • Optional: Validate duplication between GameLoop and GameOrchestrator methods.      
  • Optional: Add front-end adapter tests for events format.
  • Optional: Provide “stop after N turns” for manual testing.
  • Optional: Think about concurrency if you later add parallelism.
  • Optional: Keep function-call guidance in prompt minimal to avoid token waste.      
  • Optional: Provide LLM trace logs gated by env for debugging.
  • Optional: Monitor token usage and cost.
  • Optional: Gate manual agent prints behind a flag.
  • Optional: Add doc on adding new world YAML.
  • Optional: Ensure load_dotenv in HTTP server works across envs.
  • Optional: Verify CORS config is acceptable.
  • Optional: Add /health and /ready.
  • Optional: Document engine caching behavior.
  • Optional: Reconcile GameEvent ID generation approach.
  • Optional: Provide CLI to validate YAMLs.
  • Optional: Add id mapping for agent_id -> character_name if they diverge.
  • Optional: Single source of truth for system prompt. Right now OK.
  • Optional: Verify ends_turn default True across all actions.
  • Optional: Replace prints with logs where applicable.
  • Optional: Enforce max number of recent actions in KaniAgent.
  • Optional: Avoid None returns for schema; you already guard that.
  • Optional: Ensure anthopic engine parameters match Kani’s expectations.
  • Optional: Provide in-tests “fake engine” returning deterministic function calls.   
  • Optional: Add comment: Manual agent currently disabled.
  • Optional: Add targeted unit tests for EngineFactory.validate_config.
  • Optional: Ensure empty /agent_act/next returns empty list, not error.
  • Optional: Consider switching sleep to asyncio.Event-driven loop.
  • Optional: Review error propagation policy; current logs ok.
  • Optional: Confirm time fields use timezone consistently.
  • Optional: Provide telemetry toggles.
  • Optional: Clean up double-underscored names if any.
  • Optional: Consider state snapshots in events for replay.
  • Optional: Add version headers to API.
  • Optional: Provide test seed for reproducibility.
  • Optional: Use dataclass frozen where appropriate.
  • Optional: Ensure devs know how to run with uv.
  • Optional: Add minimal integration test to CI pipeline.
  • Optional: Ensure comments/docstrings reflect current behavior post-refactor.       
  • Optional: Document differences vs legacy architecture.
  • Optional: Keep code style consistent; current readability is good.
  • Optional: Provide security notice for plugin “custom class”.
  • Optional: Prevent blocking print in ManualAgent.
  • Optional: Guard against missing game._last_executed_action.
  • Optional: Provide docstring for GameOrchestratorAgentExecutor.
  • Optional: Validate loader fallback behavior.
  • Optional: Consider a “dry run” for agents on startup to validate config.
  • Optional: Allow agent restart without orchestrator reset.
  • Optional: Consider graceful shutdown of bus processing task.
  • Optional: Leak checks for background tasks.
  • Optional: Add sample configs for Anthropic.
  • Optional: Expand test coverage for YAML world builder.
  • Optional: Provide CLI to spawn a single tick.
  • Optional: Constrain known provider strings.
  • Optional: Use typed dicts for event metadata if helpful.
  • Optional: Add fallback if schema_exporter missing.
  • Optional: Normalize timestamps to UTC.
  • Optional: Make unserved-event consumer ID configurable.
  • Optional: Provide masking for API keys in logs.
  • Optional: Validate presence of agents defined in world.
  • Optional: Run flake8/mypy pre-commit.
  • Optional: Confirm requirements.txt includes pydantic matching used features.       
  • Optional: Evaluate memory footprint over long sessions.
  • Optional: Ensure that actions always set house_action.
  • Optional: Note: everything else looks strong.
  • The refactor is strong: clean layering, Kani usage, event bus, and config-driven   
    setup are on point.
  • Fix the initial world state injection for Kani agents, unify agent_id vs
    character_name usage, remove the duplicate AgentStrategy protocol, and move the    
    SSL hack out of KaniAgent. After these, the refactor will be production-grade.