'''
This module contains commands for interacting with the drone.
A command contains two aspects:
    1. The string representation of the command to send
    2. A formatter that handles the string response from the drone.
'''


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


class RTFM(Exception):
    def __init__(self, message) -> None:
        super().__init__(f'\nUsage: {message}')


def ok_err_fmt(resp: str) -> None:
    if resp.startswith('unknown command: '):
        cmd = resp.lstrip('unknown command: ')
        raise ValueError(f'Unknown command: {cmd}')
    
    elif resp.startswith('error'):
        raise RuntimeError('Drone reported an error')


def command() -> Tuple[str, Fmt]:
    '''Enter SDK mode.'''
    
    return 'command', ok_err_fmt


def takeoff() -> Tuple[str, Fmt]:
    '''Auto takeoff.'''

    return 'takeoff', ok_err_fmt


def land() -> Tuple[str, Fmt]:
    '''Auto landing.'''

    return 'land', ok_err_fmt


def streamon() -> Tuple[str, Fmt]:
    '''Enable video stream.'''
    
    return 'streamon', ok_err_fmt


def streamoff() -> Tuple[str, Fmt]:
    '''Disable video stream.'''

    return 'streamoff', ok_err_fmt


def emergency() -> Tuple[str, Fmt]:
    '''Stop motors immediately.'''

    return 'emergency', ok_err_fmt


def up(x: int) -> Tuple[str, Fmt]:
    '''
    Ascend by {x} cm, where
        20 <= x <= 500
    '''


    if not 20 <= x <= 500:
        raise RTFM(up.__doc__)

    return f'up {x}', ok_err_fmt


def down(x: int) -> Tuple[str, Fmt]:
    '''
    Descend by {x} cm, where
        20 <= x <= 500
    '''

    if not 20 <= x <= 500:
        raise RTFM(down.__doc__)
    
    return f'down {x}', ok_err_fmt


def left(x: int) -> Tuple[str, Fmt]:
    '''
    Fly left for {x} cm, where
        20 <= x <= 500
    '''
    
    if not 20 <= x <= 500:
        raise RTFM(left.__doc__)

    return f'left {x}', ok_err_fmt


def right(x: int) -> Tuple[str, Fmt]:
    '''
    Fly right for {x} cm, where
        20 <= x <= 500
    '''

    if not 20 <= x <= 500:
        raise RTFM(right.__doc__)

    return f'right {x}', ok_err_fmt


def forward(x: int) -> Tuple[str, Fmt]:
    '''
    Fly forward for {x} cm, where
        20 <= x <= 500
    '''

    if not 20 <= x <= 500:
        raise RTFM(forward.__doc__)

    return f'forward {x}', ok_err_fmt


def back(x: int) -> Tuple[str, Fmt]:
    '''
    Fly backward for {x} cm, where
        20 <= x <= 500
    '''

    if not 20 <= x <= 500:
        raise RTFM(forward.__doc__)

    return f'back {x}', ok_err_fmt


def cw(x: int) -> Tuple[str, Fmt]:
    '''
    Rotate {x} degrees clockwise, where
        1 <= x <= 360
    '''

    if not 1 <= x <= 360:
        raise RTFM(cw.__doc__)

    return f'cw {x}', ok_err_fmt


def ccw(x: int) -> Tuple[str, Fmt]:
    '''
    Rotate {x} degrees counterclockwise, where
        1 <= x <= 360
    '''

    if not 1 <= x <= 360:
        raise RTFM(ccw.__doc__)

    return f'ccw {x}', ok_err_fmt


def flip(direction: FlipDirection) -> Tuple[str, Fmt]:
    '''Flip in {direction} direction.'''

    return f'flip {direction}', ok_err_fmt


def go(
    x: int,
    y: int,
    z: int,
    speed: int,
    mid: Optional[int] = None,
) -> Tuple[str, Fmt]:
    '''
    Fly to {x} {y} {z} at {speed}(cm/s).
    If {mid} is provided, {x} {y} and {z} are relative to Mission Pad: {mid}, where
        10 <= speed <= 100
        -500 <= x <= 500
        -500 <= y <= 500
        -500 <= z <= 500
        1 <= mid <= 8

    Note: {x} {y} and {z} cannot be set between -20, 20 simultaneously.
    '''

    if not all(lambda value: -500 <= value <= 500, (x, y, z)):
        raise RTFM(go.__doc__)

    if all(lambda value: -20 <= value <= 20, (x, y, z)):
        raise RTFM(go.__doc__)
    
    if mid and not 1 <= mid <= 8:
        raise RTFM(go.__doc__)

    if not 10 <= speed <= 100:
        raise RTFM(go.__doc__)


    fmt = f'go {x} {y} {z} {speed}'
    if mid is not None:
        fmt += f' m{mid}'

    return fmt, ok_err_fmt


def stop() -> Tuple[str, Fmt]:
    '''Hovers in the air.'''

    return 'stop'

# TODO(Sarah): Do the roar / rest

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
    fmt = f'curve {x1} {y1} {z1} {x2} {y2} {z2} {speed}'
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