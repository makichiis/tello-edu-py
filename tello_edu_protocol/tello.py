from typing import (
    AsyncContextManager,
    AsyncGenerator,
    TypeAlias,
    Awaitable,
    Callable,
    Tuple,
    Any,
)
import contextlib
import asyncio
import av


from .state import DroneState


DEFAULT_TELLO_IP = '192.168.10.1'
DEFAULT_LOCALHOST = '0.0.0.0'
DEFAULT_TIMEOUT = 5.0
CONTROL_PORT = 8889
STATE_PORT = 8890
VIDEO_PORT = 11111
VIDEO_RESOLUTION = (640, 480)


class Drone:
    SendFn: TypeAlias = Callable[[str], Awaitable[str]]
    StateFn: TypeAlias = Callable[[None], Awaitable[DroneState]]
    Address: TypeAlias = Tuple[str, int]

    __slots__ = ('addr', 'send', 'state')

    def __init__(self, addr: Address, send: SendFn, state: StateFn) -> None:
        self.addr = addr
        self.send = send
        self.state = state

    async def video_feed(self) -> AsyncGenerator:
        await self.send('streamon')

        try:
            with av.open('udp://@0.0.0.0:11111') as container:
                for frame in container.decode(video=0):
                    yield frame.to_ndarray(format='bgr24')              

        finally:
            await self.send('streamoff')


class Protocol(asyncio.DatagramProtocol):
    Queue: TypeAlias = asyncio.Queue[str | DroneState]
    DatagramHandlerFn: TypeAlias = Callable[[str], Any]

    __slots__ = ('queue', 'datagram_handler')
    
    def __init__(self, datagram_handler: DatagramHandlerFn) -> None:
        self.queue = asyncio.Queue()
        self.datagram_handler = datagram_handler

    def datagram_received(self, data: bytes, _) -> None:  
        with contextlib.suppress(asyncio.exceptions.CancelledError):
            self.queue.put_nowait(self.datagram_handler(data))


async def keepalive(drone: Drone, interval: float = 14.0) -> None:
    with contextlib.suppress(asyncio.exceptions.CancelledError):
        while True:
            await drone.send('time?')
            await asyncio.sleep(interval)


def cmd_datagram_handler(data: bytes) -> str:
    return data.decode()


def state_datagram_handler(data: bytes) -> DroneState:
    return DroneState.from_raw(data.decode())


@contextlib.asynccontextmanager
async def conn(ip: str = DEFAULT_TELLO_IP) -> AsyncContextManager[Drone]:
    loop = asyncio.get_running_loop()
    addr = (ip, CONTROL_PORT)

    cmd_transport, cmd_protocol = await loop.create_datagram_endpoint(
        lambda: Protocol(cmd_datagram_handler),
        remote_addr=(addr),
        local_addr=((DEFAULT_LOCALHOST, CONTROL_PORT)),
    )

    state_transport, state_protocol = await loop.create_datagram_endpoint(
        lambda: Protocol(state_datagram_handler),
        local_addr=((DEFAULT_LOCALHOST, STATE_PORT)),
    )

    async def send(command: str) -> str:
        cmd_transport.sendto(command.encode())
        return await cmd_protocol.queue.get()

    async def state() -> DroneState:
        return await state_protocol.queue.get()

    try:
        drone = Drone(addr, send, state) 
        await drone.send('command')

        keepalive_task = asyncio.create_task(cmd_protocol.keepalive(drone))

        yield drone

    finally:
        keepalive_task.cancel()
        await asyncio.wait({keepalive_task}, timeout=0)

        cmd_transport.close()
        state_transport.close()
