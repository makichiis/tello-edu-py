#!/usr/bin/python

import asyncio
import tello
import cv2

async def main() -> None:
    cap = cv2.VideoCapture('udp://@0.0.0.0:1111')
    
    async with tello.conn() as drone:
        await drone.send('command')
        print(await drone.send('streamon'))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow('Tello Video Stream', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        await drone.send('streamoff')

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        ...
