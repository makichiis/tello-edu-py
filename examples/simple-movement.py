#!/usr/bin/python

import asyncio
import tello_edu_protocol as tello

async def main() -> None:
    async with tello.conn() as drone:
        print(f"Battery: {await drone.send('battery?')}")
        await drone.send('takeoff')
        await asyncio.sleep(2)
        await drone.send('cw', 180)
        await drone.send('forward', 200)
        await asyncio.sleep(2)
        await drone.send('cw', 180)
        await drone.send('forward', 200)
        await asyncio.sleep(2)
        await drone.send("land")

if __name__ == '__main__':
    asyncio.run(main())
