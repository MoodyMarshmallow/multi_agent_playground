from typing import Protocol, Any

class HouseActionProtocol(Protocol):
    def __init__(self, game: Any, command: str):
        ...

    def check_preconditions(self) -> bool:
        ...

    def apply_effects(self) -> None:
        ... 