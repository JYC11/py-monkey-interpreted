from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.object.object import Object


class Environment:
    def __init__(self, outer: Optional["Environment"] = None):
        self.store: dict[str, "Object"] = {}
        self.outer = outer

    def get(self, name: str) -> tuple[Optional["Object"], bool]:
        obj: "Object" | None = self.store.get(name)
        if obj is None and self.outer is not None:
            return self.outer.get(name)
        return obj, obj is not None

    def set(self, name: str, val: "Object") -> "Object":
        self.store[name] = val
        return val


def new_enclosed_environment(outer: Environment) -> Environment:
    env = Environment(outer=outer)
    return env


def new_environment() -> Environment:
    return Environment()
