#!/usr/bin/python

import asyncio
import tello_edu_protocol as tello

async def main() -> None:
    async with tello.conn() as drone:
        print(f"Battery: {await drone.send('battery?')}")

if __name__ == '__main__':
    asyncio.run(main())
