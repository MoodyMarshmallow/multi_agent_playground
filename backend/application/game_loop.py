"""Application layer game loop scheduler."""

import asyncio
from typing import Optional, Dict, Any, List

from ..domain.services.game_simulation import GameSimulation
from ..domain.config.schema import AgentActionOutput


class GameLoop:
    """Wraps :class:`GameSimulation` with scheduling capabilities."""

    def __init__(self, simulation: Optional[GameSimulation] = None, agent_config: Optional[Dict[str, str]] = None):
        self.simulation = simulation or GameSimulation(agent_config)
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.turn_delay = 1

    async def start(self):
        if not self.is_running:
            await self.simulation.initialize()
            self.is_running = True
            self.task = asyncio.create_task(self._run())

    async def _run(self):
        while self.is_running:
            await self.simulation.run_turn()
            await asyncio.sleep(self.turn_delay)

    async def stop(self):
        if self.is_running and self.task:
            self.is_running = False
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def reset(self):
        await self.stop()
        await self.start()

    # Proxy methods to simulation
    def set_agent_config(self, config: Dict[str, str]):
        self.simulation.set_agent_config(config)

    def get_agent_config(self) -> Dict[str, str]:
        return self.simulation.get_agent_config()

    def get_world_state(self) -> Dict[str, Any]:
        return self.simulation.get_world_state()

    def get_agent_state(self, agent_id: str) -> Dict[str, Any]:
        return self.simulation.get_agent_state(agent_id)

    def get_all_objects(self) -> List[Dict]:
        return self.simulation.get_all_objects()

    def get_game_status(self) -> Dict[str, Any]:
        return self.simulation.get_game_status()

    def get_unserved_events(self) -> List[AgentActionOutput]:
        return self.simulation.get_unserved_events()

    def get_events_since(self, timestamp: str) -> List[AgentActionOutput]:
        return self.simulation.get_events_since(timestamp)
