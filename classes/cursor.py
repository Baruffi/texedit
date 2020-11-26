
from collections import deque
from typing import Tuple

import pygame


class Cursor(object):
    def __init__(self, surface: pygame.Surface, x: int, y: int, *animation: pygame.Surface):
        self.surface = surface
        self.x = x
        self.y = y
        self.animation = deque(animation)

    def getSurface(self):
        return self.surface

    def setSurface(self, surface: pygame.Surface):
        self.surface = surface

    def updateSurface(self):
        if self.animation:
            self.animation.append(self.surface)
            self.surface = self.animation.popleft()

    def getX(self):
        return self.x

    def setX(self, x: int):
        self.x = x

    def getY(self):
        return self.y

    def setY(self, y: int):
        self.y = y

    def getPosition(self):
        return self.x, self.y

    def setPosition(self, position: Tuple[int, int]):
        self.x, self.y = position
