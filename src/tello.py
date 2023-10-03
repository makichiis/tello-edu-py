from typing import AsyncGenerator, TypeAlias, Awaitable, Callable
from contextlib import asynccontextmanager
from state import DroneState
import asyncio


DEFAULT_TELLO_IP = '192.168.10.1'
DEFAULT_TIMEOUT = 5.0
CONTROL_PORT = 8889
STATE_PORT = 8890


class TelloProtocol(asyncio.DatagramProtocol):
    DatagramHandlerFn: TypeAlias = Callable[[asyncio.Future, bytes], None]


    __slots__ = 'future', 'timeout', 'datagram_handler'


    def __init__(self, timeout: float, datagram_handler: DatagramHandlerFn) -> None:
        self.timeout = timeout
        self.future = asyncio.Future()
        self.datagram_handler = datagram_handler


    def error_received(self, exc: Exception) -> None:
        if not self.future.done():
            self.future.set_exception(exc)


    def datagram_received(self, data: bytes, _) -> None:
        self.datagram_handler(self.future, data)


    async def wait_response(self) -> asyncio.Future:
        try:
            return await asyncio.wait_for(self.future, timeout=self.timeout)
        
        except asyncio.TimeoutError as e:
            self.future.set_exception(e)
            return await self.future

        finally:
            self.future = asyncio.Future()


def command_datagram_received(future: asyncio.Future, data: bytes) -> None:
    if future.done():
        return
        
    match data.decode():
        case decoded if decoded.startswith('unknown command'):
            cmd = decoded.strip('unknown command: ')
            future.set_exception(ValueError(f'Unknown command: {cmd}'))
            
        case decoded if decoded.startswith('error'):
            future.set_exception(RuntimeError('Drone reported an error'))
        
        case decoded:
            future.set_result(decoded)


def state_datagram_received(future: asyncio.Future, data: bytes) -> None:
    if future.done():
        return
        
    try:
        state = DroneState.from_raw(data.decode())
        future.set_result(state)
            
    except Exception as e:
        future.set_exception(e)


class Drone:
    SendFn: TypeAlias = Callable[[str], Awaitable[str]]
    StateFn: TypeAlias = Callable[[None], Awaitable[str]]


    __slots__ = 'ip', 'send', 'state'


    def __init__(self, ip: str, send: SendFn, state: StateFn) -> None:
        self.ip = ip
        self.send = send
        self.state = state


@asynccontextmanager
async def conn(
    ip: str = DEFAULT_TELLO_IP,
    timeout=DEFAULT_TIMEOUT,
) -> AsyncGenerator[Drone, None]:
    loop = asyncio.get_running_loop()

    cmd_transport, cmd_protocol = await loop.create_datagram_endpoint(
        lambda: TelloProtocol(timeout, command_datagram_received),
        remote_addr=((ip, CONTROL_PORT)),
        local_addr=(('0.0.0.0', CONTROL_PORT)),
    )
        
    async def send(command: str) -> str:
        cmd_transport.sendto(command.encode())
        return await cmd_protocol.wait_response()


    state_transport, state_protocol = await loop.create_datagram_endpoint(
        lambda: TelloProtocol(timeout, state_datagram_received),
        local_addr=(('0.0.0.0', STATE_PORT)),
    )

    async def state() -> DroneState:
        return await state_protocol.wait_response()
    
    try:
        yield Drone(ip, send, state)

    finally:
        cmd_transport.close()
        state_transport.close()
        