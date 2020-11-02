from typing import Callable, Dict, Tuple
from collections import deque
import pygame


class Drawable(object):

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


class Editor(object):

    def __init__(self, cursor: Drawable, canvas: Canvas, unit_size_x: int = 1, unit_size_y: int = 1, grid_size: int = 2):
        self.cursor = cursor
        self.canvas = canvas
        self.unit_size_x = max(unit_size_x, 1)
        self.unit_size_y = max(unit_size_y, 1)
        self.grid_size = max(grid_size, 2)

    def getCursor(self):
        return self.cursor

    def getCanvas(self):
        return self.canvas

    def getUnitSizeX(self):
        return self.unit_size_x

    def getUnitSizeY(self):
        return self.unit_size_y

    def getWidth(self):
        return self.unit_size_x * self.grid_size

    def getHeight(self):
        return self.unit_size_y * self.grid_size

    def getLimitX(self):
        return self.unit_size_x * (self.grid_size - 1)

    def getLimitY(self):
        return self.unit_size_y * (self.grid_size - 1)

    def resetCanvas(self):
        self.canvas.setDrawables({})

    def scrollUp(self):
        self.canvas.updatePositions(0, self.unit_size_y)

    def scrollDown(self):
        self.canvas.updatePositions(0, -self.unit_size_y)

    def setCursorPosition(self, x: int = None, y: int = None):
        if x == None and y == None:
            pass
        elif x == None:
            self.cursor.setY(y)
        elif y == None:
            self.cursor.setX(x)
        else:
            self.cursor.setPosition((x, y))

    def moveCursorLeft(self):
        cursor_x = self.cursor.getX()

        self.cursor.setX(cursor_x - self.unit_size_x)

    def moveCursorRight(self):
        cursor_x = self.cursor.getX()

        self.cursor.setX(cursor_x + self.unit_size_x)

    def moveCursorUp(self):
        cursor_y = self.cursor.getY()

        self.cursor.setY(cursor_y - self.unit_size_y)

    def moveCursorDown(self):
        cursor_y = self.cursor.getY()

        self.cursor.setY(cursor_y + self.unit_size_y)

    def moveCursorBackwards(self):
        cursor_x, cursor_y = self.cursor.getPosition()
        limit_x = self.getLimitX()

        if cursor_x > 0:
            self.moveCursorLeft()
        else:
            self.cursor.setX(limit_x)

            if cursor_y > 0:
                self.moveCursorUp()
            else:
                self.scrollUp()

    def moveCursorForwards(self):
        cursor_x, cursor_y = self.cursor.getPosition()
        limit_x = self.getLimitX()
        limit_y = self.getLimitY()

        if cursor_x < limit_x:
            self.moveCursorRight()
        else:
            self.cursor.setX(0)

            if cursor_y < limit_y:
                self.moveCursorDown()
            else:
                self.scrollDown()

    def moveCursorUpwards(self):
        cursor_y = self.cursor.getY()

        if cursor_y > 0:
            self.moveCursorUp()
        else:
            self.scrollUp()

    def moveCursorDownwards(self):
        cursor_y = self.cursor.getY()
        limit_y = self.getLimitY()

        if cursor_y < limit_y:
            self.moveCursorDown()
        else:
            self.scrollDown()

    def editUnderCursor(self, surface: pygame.Surface):
        position = self.cursor.getPosition()
        new_field_id = 'empty' + str(self.canvas.getLength())

        under_cursor = self.canvas.getIdByPosition(position) or new_field_id

        self.canvas.updateOrCreate(under_cursor, surface, position)


class TextEditor(Editor):
    def __init__(self, canvas: Canvas, font: pygame.font.Font, grid_size: int = 2):
        cursor_surface = font.render('|', False, (255, 255, 255), (0, 0, 0))
        flash_surface = font.render(' ', False, (255, 255, 255), (0, 0, 0))
        cursor = Drawable(cursor_surface, 0, 0, flash_surface)

        unit_size_x, unit_size_y = cursor_surface.get_width(), cursor_surface.get_height()

        super().__init__(cursor, canvas, unit_size_x, unit_size_y, grid_size)

        character_dict: Dict[str, pygame.Surface] = {}
        characters = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasadfghjklzxcvbnm,.;:\\/[]{}()0123456789*+-=<>_&%$#@!?"\'´`~^ '

        character_dict[''] = pygame.Surface((unit_size_x, unit_size_y))

        for character in characters:
            character_dict[character] = font.render(
                character, False, (255, 255, 255), (255, 0, 255))

        self.characters = character_dict

        self.cursor

    def getCharacters(self):
        return self.characters

    def getCharacter(self, character: str):
        if character in self.characters.keys():
            return self.characters[character]
        else:
            return None

    def getEmptyCharacter(self):
        return self.characters['']

    def fillString(self, string: str):
        for character in string:
            if character in '\x00\r':
                continue

            space_character = self.getCharacter(' ')
            if space_character:
                if character == '\t':
                    tab = 4
                    for _ in range(tab):
                        self.editUnderCursor(space_character)
                        self.moveCursorForwards()
                    continue

            empty_character = self.getEmptyCharacter()
            if character == '\n':
                new_line = self.getWidth() - self.getCursor().getX()
                new_line = new_line // self.getUnitSizeX()
                for _ in range(new_line):
                    self.editUnderCursor(empty_character)
                    self.moveCursorForwards()
                continue

            character_surface = self.getCharacter(character)
            if character_surface:
                self.editUnderCursor(character_surface)
                self.moveCursorForwards()

    def cursorFlash(self):
        self.cursor.updateSurface()
