#!/usr/bin/python

from tello_edu_protocol import conn
import asyncio
import pygame
import sys


async def main() -> None:
    async with conn() as drone:
        pygame.init()
        flags = pygame.DOUBLEBUF | pygame.OPENGL
        screen = pygame.display.set_mode((640, 480), flags)
        pygame.display.set_caption('Drone Feed')

        try:
            async for frame in drone.video_feed():
                frame = pygame.surfarray.make_surface(frame)

                screen.blit(frame, (0, 0))
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        break
                else:
                    continue

                break

        finally:
            pygame.quit()


if __name__ == '__main__':
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        sys.exit(0)
