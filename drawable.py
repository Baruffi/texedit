from typing import Dict, Tuple
import pygame


class Drawable(object):

    def __init__(self, surface: pygame.Surface, x: int, y: int):
        self.surface = surface
        self.x = x
        self.y = y

    def getSurface(self):
        return self.surface

    def setSurface(self, surface: pygame.Surface):
        self.surface = surface

    def getX(self):
        return self.x

    def setX(self, x: int):
        self.x = x

    def getY(self):
        return self.y

    def setY(self, y: int):
        self.y = y

    def getPosition(self):
        return (self.x, self.y)

    def setPosition(self, position: Tuple[int, int]):
        self.x, self.y = position


class Canvas(object):

    def __init__(self, drawables: Dict[str, Drawable]):
        self.drawables = drawables

    def getLength(self):
        return len(self.drawables)

    def getDrawables(self):
        return self.drawables

    def setDrawables(self, drawables: Dict[str, Drawable]):
        self.drawables = drawables

    def getDrawable(self, id: str):
        return self.drawables[id]

    def setDrawable(self, id: str, drawable: Drawable):
        self.drawables[id] = drawable

    def updateSurface(self, id: str, surface: pygame.Surface):
        self.drawables[id].setSurface(surface)

    def updatePosition(self, id: str, position: Tuple[int, int]):
        self.drawables[id].setPosition(position)

    def updateOrCreate(self, id: str, surface: pygame.Surface, position: Tuple[int, int]):
        if id in self.drawables.keys():
            self.drawables[id].setSurface(surface)
            self.drawables[id].setPosition(position)
        else:
            self.setDrawable(id, Drawable(surface, position[0], position[1]))

    def updateSurfaces(self, new_surface: pygame.Surface):
        for drawable in self.drawables.values():
            drawable.setSurface(new_surface)

    def updatePositions(self, change_x: int, change_y: int):
        for drawable in self.drawables.values():
            drawable.setPosition((drawable.getX() + change_x,
                                  drawable.getY() + change_y))

    def getIdByPosition(self, position: Tuple[int, int]):
        return next((id for id, drawable in self.drawables.items() if drawable.getPosition() == position), None)

    def draw(self, display: pygame.Surface):
        display.fill((0, 0, 0))
        for drawable in self.drawables.values():
            display.blit(drawable.getSurface(), drawable.getPosition())
