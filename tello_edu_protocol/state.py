from typing import TypeAlias, Self
from dataclasses import dataclass


Value: TypeAlias = tuple[int, int, int] | float | int


@dataclass(slots=True, frozen=True)
class DroneState:
    mid: int
    x: int
    y: int
    z: int
    mpry: tuple[int, int, int]
    pitch: int
    roll: int
    yaw: int
    vgx: int
    vgy: int
    vgz: int
    templ: int
    temph: int
    tof: int
    h: int
    bat: int
    baro: float
    time: int
    agx: float
    agy: float
    agz: float


    @staticmethod
    def from_raw(state: str) -> Self | None:
        if not state:
            return None
        
        def parse(value: str) -> Value:
            if ',' in value:
                return tuple(map(int, value.split(',')))
            
            elif '.' in value:
                return float(value)

            else:
                return int(value)
        
        attrs = {}
        for token in state.strip().strip(';').split(';'):
            name, value = token.split(':')
            attrs[name] = parse(value)
        
        return Self(**attrs)
