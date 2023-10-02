from typing import AsyncGenerator, TypeAlias, Awaitable, Self
from contextlib import asynccontextmanager
import asyncio


DEFAULT_TELLO_IP = '192.168.10.1'
CONTROL_PORT = 8889


DroneAddr: TypeAlias = tuple[str, int]


class TelloProtocol(asyncio.DatagramProtocol):
    __slots__ = 'future'

    def __init__(self) -> None:
        self.future = asyncio.Future()

    def datagram_received(self, data: bytes, addr: DroneAddr) -> None:
        _ = addr
        if not self.future.done():
            self.future.set_result(data.decode())

    def error_received(self, exc: Exception) -> None:
        if not self.future.done():
            self.future.set_exception(exc)

    async def wait_response(self) -> asyncio.Future:
        try:
            return await self.future

        finally:
            self.future = asyncio.Future()


class Drone:
    send_command: callable[[Self, str], Awaitable[str]]

    def __init__(self, ip: str) -> None:
        self.ip = ip


@asynccontextmanager
async def conn(drone_ip: str = DEFAULT_TELLO_IP) -> AsyncGenerator[Drone, None]:
    '''Instantiates and injects a Drone class with the necessary methods'''
    
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        TelloProtocol,
        local_addr=(('0.0.0.0', CONTROL_PORT))
    )
        
    async def send_command(self: Drone, command: str) -> str:
        transport.sendto(command.encode(), (self.ip, CONTROL_PORT))
        return await protocol.wait_response()
    
    drone = Drone(drone_ip)
    drone.send_command = send_command.__get__(drone, Drone)

    try:
        yield drone

    finally:
        transport.close()
