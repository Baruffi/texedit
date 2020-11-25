from collections import deque
from typing import Dict, Tuple

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


class Canvas(object):

    def __init__(self, drawables: Dict[Tuple[int, int], pygame.Surface]):
        self.drawables = drawables

    def getDrawables(self):
        return self.drawables

    def setDrawables(self, drawables: Dict[Tuple[int, int], pygame.Surface]):
        self.drawables = drawables

    def getDrawable(self, position: Tuple[int, int]):
        return self.drawables.get(position)

    def setDrawable(self, position: Tuple[int, int], surface: pygame.Surface):
        self.drawables[position] = surface

    def deleteDrawable(self, position: Tuple[int, int]):
        self.drawables.pop(position, None)

    def updatePositions(self, position: Tuple[int, int]):
        newDrawables: Dict[Tuple[int, int], pygame.Surface] = {}

        for oldPosition in self.drawables.keys():
            newPosition = tuple(map(sum, zip(oldPosition, position)))

            newDrawables[newPosition] = self.drawables.get(oldPosition)

        self.setDrawables(newDrawables)


class Editor(object):

    def __init__(self, cursor: Cursor, canvas: Canvas, unit_size_x: int = 1, unit_size_y: int = 1, grid_size_x: int = 2, grid_size_y: int = 2):
        self.cursor = cursor
        self.canvas = canvas
        self.unit_size_x = max(unit_size_x, 1)
        self.unit_size_y = max(unit_size_y, 1)
        self.grid_size_x = max(grid_size_x, 2)
        self.grid_size_y = max(grid_size_y, 2)

    def getCursor(self):
        return self.cursor

    def getCanvas(self):
        return self.canvas

    def getUnitSizeX(self):
        return self.unit_size_x

    def getUnitSizeY(self):
        return self.unit_size_y

    def getWidth(self):
        return self.unit_size_x * self.grid_size_x

    def setGridSize(self, grid_size_x: int, grid_size_y: int):
        self.grid_size_x = max(grid_size_x, 2)
        self.grid_size_y = max(grid_size_y, 2)

    def getHeight(self):
        return self.unit_size_y * self.grid_size_y

    def getLimitX(self):
        return self.unit_size_x * (self.grid_size_x - 1)

    def getLimitY(self):
        return self.unit_size_y * (self.grid_size_y - 1)

    def resetCanvas(self):
        self.canvas.setDrawables({})

    def scrollLeft(self):
        self.canvas.updatePositions((self.unit_size_x, 0))

    def scrollRight(self):
        self.canvas.updatePositions((-self.unit_size_x, 0))

    def scrollUp(self):
        self.canvas.updatePositions((0, self.unit_size_y))

    def scrollDown(self):
        self.canvas.updatePositions((0, -self.unit_size_y))

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
        cursor_x = self.cursor.getX()

        if cursor_x > 0:
            self.moveCursorLeft()
        else:
            self.scrollLeft()

    def moveCursorForwards(self):
        cursor_x = self.cursor.getX()
        limit_x = self.getLimitX()

        if cursor_x < limit_x:
            self.moveCursorRight()
        else:
            self.scrollRight()

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

        self.canvas.setDrawable(position, surface)

    def deleteUnderCursor(self):
        position = self.cursor.getPosition()

        self.canvas.deleteDrawable(position)


class TextEditor(Editor):
    def __init__(self, canvas: Canvas, font: pygame.font.Font, grid_size_x: int = 2, grid_size_y: int = 2):
        cursor_surface = font.render('|', False, (255, 255, 255), (0, 0, 0))
        flash_surface = font.render(' ', False, (255, 255, 255), (0, 0, 0))
        cursor = Cursor(cursor_surface, 0, 0, flash_surface)

        unit_size_x, unit_size_y = cursor_surface.get_width(), cursor_surface.get_height()

        super().__init__(cursor, canvas, unit_size_x, unit_size_y, grid_size_x, grid_size_y)

        character_dict: Dict[str, pygame.Surface] = {}
        characters = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasadfghjklzxcvbnm,.;:\\/[]{}()0123456789*+-=<>_&%$#@!?"\'´`~^ '

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

    def carriageReturn(self):
        cursor_position = self.cursor.getPosition()

        positions = self.canvas.getDrawables().keys()
        sorted_x = sorted([position[0] for position in positions if position[1]
                           == cursor_position[1] and position[0] <= cursor_position[0]])

        if len(sorted_x) != 0:
            final_x = sorted_x.pop()

            while final_x < 0:
                self.scrollLeft()
                final_x += self.unit_size_x

            self.cursor.setX(final_x)

            while self.canvas.getDrawable(self.cursor.getPosition()):
                self.moveCursorBackwards()

            if self.cursor.getX() == 0:
                self.scrollRight()
            else:
                self.moveCursorForwards()
        else:
            self.cursor.setX(0)

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

            if character == '\n':
                self.carriageReturn()
                self.moveCursorDownwards()
                continue

            character_surface = self.getCharacter(character)
            if character_surface:
                self.editUnderCursor(character_surface)
                self.moveCursorForwards()

    def getLine(self, cut: bool = False):
        line = ''
        canvas = self.getCanvas()
        character_items = self.getCharacters().items()

        self.carriageReturn()

        while (surface := canvas.getDrawable(self.getCursor().getPosition())):
            for character, character_surface in character_items:
                if surface == character_surface:
                    line += character
                    break

            self.moveCursorForwards()

        if cut:
            for character in line:
                self.moveCursorBackwards()
                self.deleteUnderCursor()

        return line

    def getContent(self):
        text = ''
        drawables = self.getCanvas().getDrawables().items()
        sorted_drawables_intermediate = sorted(
            [((position[1], position[0]), surface) for position, surface in drawables])
        sorted_drawables = [((position[1], position[0]), surface)
                            for position, surface in sorted_drawables_intermediate]
        character_items = self.getCharacters().items()

        last_y: int = None

        for position, surface in sorted_drawables:
            if last_y != None:
                current_y = position[1] // self.unit_size_y

                text += '\n' * (current_y - last_y)

            for character, character_surface in character_items:
                if surface == character_surface:
                    text += character
                    break

            last_y = position[1] // self.unit_size_y

        return text

    def cursorFlash(self):
        self.cursor.updateSurface()
