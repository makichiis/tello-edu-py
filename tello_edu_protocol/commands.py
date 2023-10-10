from typing import (
    TypeAlias,
    Callable,
    Optional,
    Tuple,
    Any
)
from enum import StrEnum


Fmt: TypeAlias = Callable[[str], Any]
Command: TypeAlias = Callable[[], Tuple[str, Fmt]]


class FlipDirection(StrEnum):
    Left = 'l'
    Right = 'r'
    Forward = 'f'
    Backward = 'b'


def ok_err_fmt(resp: str) -> None:
    if resp.startswith('unknown command: '):
        cmd = resp.lstrip('unknown command: ')
        raise ValueError(f'Unknown command: {cmd}')
    
    elif resp.startswith('error'):
        raise RuntimeError('Drone reported an error')


def command() -> Tuple[str, Fmt]:
    return 'command', ok_err_fmt


def takeoff() -> Tuple[str, Fmt]:
    return 'takeoff', ok_err_fmt


def land() -> Tuple[str, Fmt]:
    return 'land', ok_err_fmt


def streamon() -> Tuple[str, Fmt]:
    return 'streamon', ok_err_fmt


def streamoff() -> Tuple[str, Fmt]:
    return 'streamoff', ok_err_fmt


def emergency() -> Tuple[str, Fmt]:
    return 'emergency', ok_err_fmt


def up(x: int) -> Tuple[str, Fmt]:
    return f'up {x}', ok_err_fmt


def down(x: int) -> Tuple[str, Fmt]:
    return f'down {x}', ok_err_fmt


def left(x: int) -> Tuple[str, Fmt]:
    return f'left {x}', ok_err_fmt


def right(x: int) -> Tuple[str, Fmt]:
    return f'right {x}', ok_err_fmt


def forward(x: int) -> Tuple[str, Fmt]:
    return f'forward {x}', ok_err_fmt


def back(x: int) -> Tuple[str, Fmt]:
    return f'back {x}', ok_err_fmt


def cw(x: int) -> Tuple[str, Fmt]:
    return f'cw {x}', ok_err_fmt


def ccw(x: int) -> Tuple[str, Fmt]:
    return f'ccw {x}', ok_err_fmt


def flip(direction: FlipDirection) -> Tuple[str, Fmt]:
    return f'flip {direction}', ok_err_fmt


def go(x: int, y: int, z: int, speed: int, mid: Optional[int]) -> Tuple[str, Fmt]:
    fmt = f'go {x} {y} {z} {speed}'
    if mid is not None:
        fmt += f' m{mid}'

    return fmt, ok_err_fmt


def stop() -> Tuple[str, Fmt]:
    return 'stop'


def curve(
    x1: int,
    y1: int,
    z1: int,
    x2: int, 
    y2: int,
    z2: int,
    speed: int,
    mid: Optional[int],
) -> Tuple[str, Fmt]:
    fmt = f'curve {x1} {y1} {x2} {y2} {z2} {speed}'
    if mid is not None:
        fmt += f' m{mid}'

    return fmt, ok_err_fmt


def jump(
    x: int,
    y: int,
    z: int,
    speed: int,
    yaw: int,
    mid1: int,
    mid2: int,
) -> Tuple[str, Fmt]:
    return f'jump {x} {y} {z} {speed} {yaw} m{mid1} m{mid2}', ok_err_fmt


def speed(x: int) -> Tuple[str, Fmt]:
    return f'speed {x}'


def rc(a: int, b: int, c: int, d: int) -> Tuple[str, Fmt]:
    return f'rc {a} {b} {c} {d}'


def wifi(ssid: str, passwd: str) -> Tuple[str, Fmt]:
    return f'{ssid} {passwd}'


def mon() -> Tuple[str, Fmt]:
    return 'mon'


def moff() -> Tuple[str, Fmt]:
    return 'moff'


def mdirection(x: int) -> Tuple[str, Fmt]:
    return f'mdirection {x}'


def ap(ssid: str, passwd: str) -> Tuple[str, Fmt]:
    return f'ap {ssid} {passwd}'


def get_speed() -> Tuple[str, Fmt]:
    return 'speed?', int


def get_battery() -> Tuple[str, Fmt]:
    return 'battery?', int


def get_time() -> Tuple[str, Fmt]:
    return 'time?', str


def get_wifi() -> Tuple[str, Fmt]:
    return 'wifi?', str


def get_sdk() -> Tuple[str, Fmt]:
    return 'sdk?', str


def get_sn() -> Tuple[str, Fmt]:
    return 'sn?', str