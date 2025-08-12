"""FastAPI interface for the multi-agent playground."""

from dotenv import load_dotenv
from typing import List, Dict, Any
import argparse
import os
from contextlib import asynccontextmanager

load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware

from ..application.game_loop import GameLoop
from ..domain.services.game_simulation import GameSimulation
from ..domain.config.schema import (
    WorldStateResponse,
    GameEvent,
    GameEventList,
    StatusMsg,
    GameStatus,
    AgentStateResponse,
    GameObject,
    AgentActionOutput,
)
from ..log_config import setup_logging

verbose_mode = os.getenv("VERBOSE", "false").lower() in ("true", "1", "yes")
setup_logging(verbose=verbose_mode)

@asynccontextmanager
async def lifespan(app: FastAPI):
    simulation = GameSimulation()
    game_loop = GameLoop(simulation)
    app.state.game_loop = game_loop
    await game_loop.start()
    try:
        yield
    finally:
        await game_loop.stop()

app = FastAPI(title="Multi-Agent Playground", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_game_loop(request: Request) -> GameLoop:
    loop: GameLoop = request.app.state.game_loop
    if not loop:
        raise HTTPException(status_code=500, detail="Game not initialized")
    return loop


@app.get("/agent_act/next", response_model=List[AgentActionOutput])
async def get_latest_agent_actions(game: GameLoop = Depends(get_game_loop)):
    return game.get_unserved_events()


@app.get("/agents/states", response_model=List[AgentStateResponse])
async def get_agents_states(agent_ids: List[str], game: GameLoop = Depends(get_game_loop)):
    states = []
    for agent_id in agent_ids:
        try:
            state = game.get_agent_state(agent_id)
            states.append(AgentStateResponse(**state))
        except KeyError:
            continue
    return states


@app.get("/objects", response_model=List[GameObject])
async def get_objects(game: GameLoop = Depends(get_game_loop)):
    return [GameObject(**obj) for obj in game.get_all_objects()]


@app.get("/world_state")
async def get_world_state(game: GameLoop = Depends(get_game_loop)):
    state = game.get_world_state()
    return WorldStateResponse(**state)


@app.get("/game/events", response_model=GameEventList)
async def get_game_events(since_timestamp: str = "", game: GameLoop = Depends(get_game_loop)):
    events = game.get_events_since(since_timestamp)
    game_events = [
        GameEvent(
            id=hash(event.timestamp) if event.timestamp else 0,
            type="agent_action",
            timestamp=event.timestamp or "",
            data=event.dict(),
        )
        for event in events
    ]
    return GameEventList(events=game_events)


@app.post("/game/reset", response_model=StatusMsg)
async def reset_game(game: GameLoop = Depends(get_game_loop)):
    await game.reset()
    return StatusMsg(status="ok")


@app.get("/game/status", response_model=GameStatus)
async def get_game_status(game: GameLoop = Depends(get_game_loop)):
    return GameStatus(**game.get_game_status())


@app.post("/game/pause", response_model=StatusMsg)
async def pause_game(game: GameLoop = Depends(get_game_loop)):
    if not game.is_running:
        return StatusMsg(status="already_paused")
    await game.stop()
    return StatusMsg(status="paused")


@app.post("/game/resume", response_model=StatusMsg)
async def resume_game(game: GameLoop = Depends(get_game_loop)):
    if game.is_running:
        return StatusMsg(status="already_running")
    await game.start()
    return StatusMsg(status="resumed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent Playground Backend Server")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging (show INFO+ messages)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on (default: 8000)")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=args.port,
        reload=args.reload,
        log_level="info",
    )
