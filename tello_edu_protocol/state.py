from typing import TypeAlias, Tuple, Self
from dataclasses import dataclass


Value: TypeAlias = Tuple[int, int, int] | float | int


@dataclass(slots=True, frozen=True)
class DroneState:
    '''Structure for storing the drone state'''

    mid: int
    x: int
    y: int
    z: int
    mpry: Tuple [int, int, int]
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

    @classmethod
    def from_raw(cls, state: str) -> Self | None:
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
        for token in state.strip(';').split(';'):
            name, value = token.split(':')
            attrs[name] = parse(value)
        
        return cls(**attrs)
