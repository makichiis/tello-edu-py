from typing import (
    AsyncContextManager,
    AsyncGenerator,
    TypeAlias,
    Awaitable,
    Callable,
    Optional,
    Tuple,
    Self,
    Any,
)
import contextlib
import asyncio
import av

from .state import DroneState
from .commands import (
    streamoff,
    streamon,
    get_time,
    command,
    Command,
    Fmt,
)


DEFAULT_TELLO_IP = '192.168.10.1'
DEFAULT_LOCALHOST = '0.0.0.0'
DEFAULT_TIMEOUT = 10
CONTROL_PORT = 8889
STATE_PORT = 8890
VIDEO_PORT = 11111
VIDEO_RESOLUTION = (640, 480)


class Drone:
    '''The user api for interacting with the drone.'''
    
    SendFn: TypeAlias = Callable[[str], Awaitable[str]]
    StateFn: TypeAlias = Callable[[], Awaitable[DroneState]]
    Address: TypeAlias = Tuple[str, int]

    __slots__ = ('addr', 'send', 'state')

    def __init__(self, addr: Address, send: SendFn, state: StateFn) -> None:
        '''
        The `send` and `state` methods are both generated by a drone
        connection manager to avoid coupling and ensure encapsulation.

        Funny how a more functional style solves problems that OOP makes
        for itself. ¯\_(ツ)_/¯
        '''

        self.addr = addr
        self.send = send
        self.state = state

    async def video_feed(self) -> AsyncGenerator:
        '''
        TODO (Carter): The drone sometimes decides not to stream video
                       determine if this is software or hardware
        '''

        # Buy better drones pls :)

        await self.command(streamon)

        try:
            with av.open('udp://@0.0.0.0:11111') as container:
                for frame in container.decode(video=0):
                    yield frame.to_ndarray(format='bgr24')              

        finally:
            await self.command(streamoff)


    async def command(
        self,
        cmd: Command,
        *args,
        timeout: float = DEFAULT_TIMEOUT,
        formatter: Optional[Fmt] = None,
        **kwargs
    ) -> Any:
        '''A wrapper for running drone commands and retreiving their results.'''

        msg, fmt = cmd(*args, **kwargs)
        if formatter is not None:
            fmt = formatter

        return fmt(await self.send(msg, timeout=timeout))
        

class Protocol(asyncio.DatagramProtocol):
    '''The `low level` drone communication protocol'''

    Value: TypeAlias = str | DroneState
    Queue: TypeAlias = asyncio.Queue[Value]
    DatagramHandlerFn: TypeAlias = Callable[[Self, bytes, Drone.Address], None]

    __slots__ = ('queue', 'datagram_handler')
    
    def __init__(self, datagram_handler: DatagramHandlerFn) -> None:
        self.queue = asyncio.Queue()
        self.datagram_handler = datagram_handler

    def datagram_received(self, data: bytes, addr: Drone.Address) -> None:
        self.datagram_handler(self, data, addr)


def cmd_datagram_handler(proto: Protocol, data: bytes, _: Drone.Address) -> None:
    '''Decodes incoming data into a response'''
    
    decoded = data.decode('ASCII').strip()
    proto.queue.put_nowait(decoded)


def state_datagram_handler(proto: Protocol, data: bytes, _: Drone.Address) -> None:
    '''Serializes an incoming response to a DroneState'''

    state = DroneState.from_raw(data.decode('ASCII').strip())
    proto.queue.put_nowait(state)


def keepalive(drone: Drone) -> Callable[[], Awaitable[None]]:
    '''
    A background runner for keeping an active connection with
    the drone whilst the connection is active.

    Returns a function that will end the background task.
    '''

    async def task() -> None:
        with contextlib.suppress(asyncio.CancelledError):
            while True:
                await drone.command(get_time)
                await asyncio.sleep(10)

    keepalive_task = asyncio.create_task(task())

    async def stop() -> None:
        with contextlib.suppress(asyncio.TimeoutError):
            keepalive_task.cancel()
            await asyncio.wait({keepalive_task})

    return stop


@contextlib.asynccontextmanager
async def conn(
        ip: str = DEFAULT_TELLO_IP, 
        *, timeout: float=DEFAULT_TIMEOUT
) -> AsyncContextManager[Drone]:
    '''
    The context manager for a drone connection.
    '''
    
    loop = asyncio.get_running_loop()
    addr = (ip, CONTROL_PORT)

    # Responsible for sending and receiving UDP data to and from the drone
    cmd_transport, cmd_protocol = await loop.create_datagram_endpoint(
        lambda: Protocol(cmd_datagram_handler),
        remote_addr=(addr),
        local_addr=((DEFAULT_LOCALHOST, CONTROL_PORT)),
    )

    # Responsible for receiving state UDP data from the drone
    state_transport, state_protocol = await loop.create_datagram_endpoint(
        lambda: Protocol(state_datagram_handler),
        local_addr=((DEFAULT_LOCALHOST, STATE_PORT)),
    )

    # The generated `send method` for the Drone class
    async def send(msg: str, *, timeout: float = timeout) -> str:
        async with asyncio.timeout(timeout):
            cmd_transport.sendto(msg.encode('utf_8'))
            return await cmd_protocol.queue.get()
    
    # The generated `state method` for the Drone class
    async def state(*, timeout: float = timeout) -> DroneState:
        async with asyncio.timeout(timeout):
            return await state_protocol.queue.get()

    try:
        drone = Drone(addr, send, state)
        keepalive_stop = keepalive(drone)
        await drone.command(command)

        yield drone

    finally:
        await keepalive_stop()

        cmd_transport.close()
        state_transport.close()
