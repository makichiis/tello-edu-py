#!/usr/bin/python

import asyncio
import tello_edu_protocol as tello

async def main() -> None:
    async with tello.conn() as drone:
        battery_life = await drone.send('battery?')
        print(f"Battery: {battery_life}%")

if __name__ == '__main__':
    asyncio.run(main())
