#!/usr/bin/python3


import asyncio
import tello
import cv2
import sys
import av


async def main() -> None:
    
    async with tello.conn() as drone:
        await drone.send('command')
        await drone.send('streamon')

        await asyncio.sleep(5)

        try:
            container = av.open('udp://@0.0.0.0:11111')

            for frame in container.decode(video=0):
                img = frame.to_ndarray(format='bgr24')
                cv2.imshow('Tello Stream', img)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cv2.destroyAllWindows()
            await drone.send('streamoff')

    
if __name__ == '__main__':
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        sys.exit(0)
