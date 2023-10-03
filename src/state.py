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
    def from_raw(state: str) -> Self:
        
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

        return DroneState(**attrs)


def test_from_raw() -> None:
    state = 'mid:-1;x:0;y:0;z:0;mpry:0,0,0;pitch:0;roll:0;yaw:0;vgx:0;vgy:0;vgz:0;templ:59;temph:63;tof:6553;h:0;bat:91;baro:60.84;time:0;agx:-3.00;agy:14.00;agz:-1008.00'

    drone_state = DroneState.from_raw(state)

    assert drone_state.mid == -1
    assert drone_state.x == 0
    assert drone_state.y == 0
    assert drone_state.z == 0
    assert drone_state.mpry == (0, 0, 0)
    assert drone_state.pitch == 0
    assert drone_state.yaw == 0
    assert drone_state.vgx == 0
    assert drone_state.vgy == 0
    assert drone_state.vgz == 0
    assert drone_state.templ == 59
    assert drone_state.temph == 63
    assert drone_state.tof == 6553
    assert drone_state.h == 0
    assert drone_state.bat == 91
    assert drone_state.baro == 60.84
    assert drone_state.time == 0
    assert drone_state.agx == -3.00
    assert drone_state.agy == 14.00
    assert drone_state.agz == -1008.00
