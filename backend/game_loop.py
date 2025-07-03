import threading
import time
from backend.text_adventure_games.games import Game
from backend.text_adventure_games.things import Character
from backend.config.schema import PlanActionResponse, AgentActionOutput, AgentPerception, PerceiveBackendAction
from datetime import datetime
from backend.text_game_old.canonical_world import build_canonical_house_environment

# this is just a placeholder for the game loop
# TODO: We will need to implement the specific details of game loop to handle the game logic

class GameLoop:
    def __init__(self, step_seconds=1):
        self.game = self._build_game()
        self.tick_count = 0
        self.running = False
        self.action_log = []  # Stores dicts or PlanActionResponse
        self.lock = threading.Lock()
        self.step_seconds = step_seconds

    def _build_game(self):
        # Use the canonical house environment for a valid world setup
        return build_canonical_house_environment()

    def plan_and_log_actions(self):
        """
        Advance one step for all agents, log the actions.
        """
        for agent_id in self.game.active_agents:
            plan = self.plan_next_action(agent_id)
            with self.lock:
                self.action_log.append({
                    "tick": self.tick_count,
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent_id": agent_id,
                    "plan": plan
                })

    def plan_next_action(self, agent_id: str) -> PlanActionResponse:
        agent = self.game.characters[agent_id]
        perception = self.game.get_world_state_for_agent(agent)
        # Use a valid PerceiveBackendAction as a placeholder
        action = AgentActionOutput(
            agent_id=agent_id,
            action=PerceiveBackendAction(action_type="perceive"),
            emoji="🤖",
            timestamp=datetime.utcnow().isoformat(),
            current_room=perception['location']['name']
        )
        return PlanActionResponse(action=action, perception=AgentPerception(**perception))

    def run(self):
        """
        Run the game loop in the background.
        """
        self.running = True
        while self.running:
            self.plan_and_log_actions()
            self.tick_count += 1
            time.sleep(self.step_seconds)

    def start_background_loop(self):
        """
        Start the game loop as a background thread.
        """
        t = threading.Thread(target=self.run, daemon=True)
        t.start()

    def get_recent_actions(self, since_tick=None, since_timestamp=None):
        """
        Return list of recent actions since a certain tick or timestamp.
        """
        with self.lock:
            if since_tick is not None:
                return [entry for entry in self.action_log if entry["tick"] > since_tick]
            elif since_timestamp is not None:
                return [entry for entry in self.action_log if entry["timestamp"] > since_timestamp]
            else:
                # default: last 50 actions
                return self.action_log[-50:]

# Singleton instance
game_loop = GameLoop()
