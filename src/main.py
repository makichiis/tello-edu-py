#!/usr/bin/python

import asyncio
import tello

async def main() -> None:
    async with tello.conn() as drone:
        print(await drone.send_command('command'))
        print(await drone.send_command('battery?'))


if __name__ == '__main__':
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        ...
