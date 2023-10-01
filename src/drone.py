from typing import TypeAlias, AsyncGenerator
from contextlib import asynccontextmanager
from functools import partial

import asyncio

CONTROL_PORT = 8889
Drone: TypeAlias = tuple[str, int]
MessageCallback: TypeAlias = asyncio.Queue[tuple[str, Drone]]


async def send_command(
    transport: asyncio.DatagramTransport,
    on_con_msg: MessageCallback,
    drone: Drone,
    command: str,
) -> tuple[str, Drone] | None:
    transport.sendto(command.encode(), drone)

    try:
        return await asyncio.wait_for(on_con_msg.get(), timeout=5)
    
    except asyncio.TimeoutError:
        return None


async def on_recv(
    on_con_msg: MessageCallback,
    data: bytes,
    addr: Drone,
) -> None:
    on_con_msg.put_nowait((data.decode(), addr))


@asynccontextmanager
async def conn(ip: str = '192.168.10.1') -> AsyncGenerator:
    loop = asyncio.get_running_loop()
    on_con_msg: MessageCallback = asyncio.Queue()

    class Proto(asyncio.DatagramProtocol):
        def datagram_received(self, data: bytes, addr: Drone):
            loop.create_task(on_recv(on_con_msg, data, addr))

    transport, _ = await loop.create_datagram_endpoint(
        lambda: Proto(),
        local_addr=('0.0.0.0', CONTROL_PORT),
    )

    try:
        yield partial(send_command, transport, on_con_msg, (ip, CONTROL_PORT)) 

    finally:
        transport.close()
