from dataclasses import dataclass


@dataclass(frozen=True)
class Health:
    status: str
    version: str
