#!/usr/bin/python

import asyncio
import tello_edu_protocol as tello
from tello_edu_protocol.commands import get_battery

async def main() -> None:
    async with tello.conn() as drone:
        battery_life = await drone.command(get_battery)
        print(f"Battery: {battery_life}%")

if __name__ == '__main__':
    asyncio.run(main())
