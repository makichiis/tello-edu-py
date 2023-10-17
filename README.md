# tello-edu-py
Tello EDU 2.0 SDK API implemented in Python.
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

# Building
1. Install build dependencies
```sh
~/tello-edu-py $ pip install -r requirements/build
```
2. Build as a module via `pip`
```sh
~/tello-edu-py $ pip install . # must be in root of project
```

# Usage
Since this is a wrapper library for the Tello EDU protocol, follow instructions for
setting up a Tello EDU drone before proceeding.

Examples of how the `tello-edu-protocol` library is used can be found
under `examples/`.
Simple example with movement:
```py
import asyncio
import tello_edu_protocol as tello
from tello_edu_protocol.commands import (
    takeoff,
    cw,
    forward,
    land
)


async def main() -> None:
    # timeout in seconds (20s) means that the library will
    # wait 20 seconds for a response before throwing an error.
    # Every command called for `drone` shares this timeout duration.
    # Command list can be found under `tello-edu-protocol/commands.py`
    # and corresponds to the SDK documentation.
    async with tello.conn(timeout=20) as drone:
        await drone.command(takeoff)      # send takeoff command
	await drone.command(forward, 40)  # fly forward 40cm
	await drone.command(cw, 180)      # turn around (180deg)
	await drone.command(forward, 40)  # fly forward 40cm
	await drone.command(land)         # land drone


if __name__ == '__main__':
    asyncio.run(main())
```

# Contributing
While this project is intended for use by our lab group, contributions are welcome.

1. Clone this repository
```sh
~ $ git clone https://github.com/zaruhev/tello-edu-py
```
2. In `tello-edu-py`, install dev dependencies
```sh
~/tello-edu-py $ pip install -r requirements/dev
``` 

# Changelog
v0.2.0 - Added functional components for the drone commands. See examples.
