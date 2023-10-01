#!/usr/bin/python

import asyncio
import drone

async def main() -> None:
    async with drone.conn() as send:

        match await send('command'):
            case (str('ok'), _):
                ...
            case _:
                raise Exception('lol')


        match await send('battery?'):
            case (str(data), _):
                print(f'Battery level: {data}')
            case _:
                raise Exception('lol')


if __name__ == '__main__':
    asyncio.run(main())
