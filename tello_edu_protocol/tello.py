from typing import AsyncContextManager, TypeAlias, Callable, Awaitable, AsyncGenerator
from contextlib import asynccontextmanager, suppress
import asyncio
import av


DEFAULT_TELLO_IP = '192.168.10.1'
DEFAULT_TIMEOUT = 5.0
CONTROL_PORT = 8889
STATE_PORT = 8890
VIDEO_PORT = 11111
VIDEO_RESOLUTION = (640, 480)


class Protocol(asyncio.DatagramProtocol):
    Queue: TypeAlias = asyncio.Queue[str]
    DatagramHandlerFn: TypeAlias = Callable[[Queue, bytes], None]


    __slots__ = ('queue', 'datagram_handler')


    def __init__(self, datagram_handler: DatagramHandlerFn) -> None:
        self.queue = asyncio.Queue()
        self.datagram_handler = datagram_handler


    def datagram_received(self, data: bytes, _) -> None:
        with suppress(asyncio.exceptions.CancelledError):
            self.datagram_handler(self.queue, data)


def cmd_datagram_handler(queue: Protocol.Queue, data: bytes) -> None:
    queue.put_nowait(data.decode())


def state_datagram_handler(queue: Protocol.Queue, data: bytes) -> None:
    ...


class Drone:
    Send: TypeAlias = Callable[[str], Awaitable[str]]
    Address: TypeAlias = tuple[str, int]


    __slots__ = ('addr', 'send')


    def __init__(self, addr: Address, send: Send) -> None:
        self.addr = addr
        self.send = send


    async def video_feed(self) -> AsyncGenerator:
        print('Starting Stream: ', await self.send('streamon'))

        try:
            with av.open('udp://@0.0.0.0:11111') as container:
                for frame in container.decode(video=0):
                    yield frame.to_ndarray(format='bgr24')

        finally:
            print('Ending Stream', await self.send('streamoff'))


async def keepalive(drone: Drone, interval: float = 14.0) -> None:
    with suppress(asyncio.exceptions.CancelledError):
        while True:
            await drone.send('time?')
            await asyncio.sleep(interval)


@asynccontextmanager
async def conn(ip: str = DEFAULT_TELLO_IP) -> AsyncContextManager[Drone]:
    loop = asyncio.get_running_loop()
    addr = (ip, CONTROL_PORT)

    cmd_transport, cmd_protocol = await loop.create_datagram_endpoint(
        lambda: Protocol(cmd_datagram_handler),
        remote_addr=(addr),
        local_addr=(('0.0.0.0', CONTROL_PORT)),
    )

    state_transport, _ = await loop.create_datagram_endpoint(
        lambda: Protocol(state_datagram_handler),
        local_addr=(('0.0.0.0', STATE_PORT)),
    )

    async def send(command: str) -> str:
        cmd_transport.sendto(command.encode())
        return await cmd_protocol.queue.get()

    try:
        drone = Drone(addr, send)
        await drone.send('command')

        keepalive_task = asyncio.create_task(keepalive(drone))

        yield drone

    finally:
        keepalive_task.cancel()
        await asyncio.wait({keepalive_task}, timeout=0)

        cmd_transport.close()
        state_transport.close()
