from collections import deque
from typing import Deque, Dict, Tuple

import pygame
from utils.surface import getScaled, getTinted

from classes.canvas import Canvas
from classes.cursor import Cursor


class Editor(object):

    def __init__(self, cursor: Cursor, canvas: Canvas, tint: Tuple[int, ...] = (0, 0, 0), unit_size_x: int = 1, unit_size_y: int = 1, grid_size_x: int = 2, grid_size_y: int = 2):
        self.cursor = cursor
        self.canvas = canvas
        self.tint = tint
        self.unit_size_x = max(unit_size_x, 1)
        self.unit_size_y = max(unit_size_y, 1)
        self.grid_size_x = max(grid_size_x, 2)
        self.grid_size_y = max(grid_size_y, 2)

    def getCursor(self):
        return self.cursor

    def getCanvas(self):
        return self.canvas

    def getTint(self):
        return self.tint

    def getUnitSizeX(self):
        return self.unit_size_x

    def getUnitSizeY(self):
        return self.unit_size_y

    def getUnitSizes(self):
        return self.unit_size_x, self.unit_size_y

    def setUnitSizes(self, unit_size_x: int, unit_size_y: int):
        self.unit_size_x = max(unit_size_x, 1)
        self.unit_size_y = max(unit_size_y, 1)

    def getGridSizes(self):
        return self.grid_size_x, self.grid_size_y

    def setGridSizes(self, grid_size_x: int, grid_size_y: int):
        self.grid_size_x = max(grid_size_x, 2)
        self.grid_size_y = max(grid_size_y, 2)

    def getWidth(self):
        return self.unit_size_x * self.grid_size_x

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
            return False
        else:
            self.scrollLeft()
            return True

    def moveCursorForwards(self):
        cursor_x = self.cursor.getX()
        limit_x = self.getLimitX()

        if cursor_x < limit_x:
            self.moveCursorRight()
            return False
        else:
            self.scrollRight()
            return True

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
        scaled_surface = getScaled(
            surface, (self.unit_size_x, self.unit_size_y))
        tinted_surface = getTinted(scaled_surface, self.tint)

        self.canvas.setDrawable(position, tinted_surface)

    def deleteUnderCursor(self):
        position = self.cursor.getPosition()

        self.canvas.deleteDrawable(position)


class TextEditor(Editor):
    def __init__(self, font: pygame.font.Font, grid_size_x: int = 2, grid_size_y: int = 2):
        cursor_surface = font.render(
            '|', False, (255, 255, 255), (0, 0, 0))
        flash_surface = font.render(' ', False, (255, 255, 255), (0, 0, 0))

        cursor = Cursor(cursor_surface, 0, 0, flash_surface)
        canvas = Canvas({})
        tints: Deque[Tuple[int, ...]] = deque([(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
                                               (255, 255, 0), (255, 0, 255), (0, 255, 255)])
        unit_size_x = cursor_surface.get_width()
        unit_size_y = cursor_surface.get_height()

        super().__init__(cursor, canvas, tints[0], unit_size_x,
                         unit_size_y, grid_size_x, grid_size_y)

        character_dict: Dict[str, pygame.Surface] = {}
        characters = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasadfghjklzxcvbnm,.;:\\/[]{}()0123456789*+-=<>_&%$#@!?"\'´`~^ '

        for character in characters:
            character_dict[character] = font.render(
                character, False, (255, 255, 255), (0, 0, 0))

        self.characters = character_dict

        self.tints = tints

    def getCharacters(self):
        return self.characters

    def getCharacter(self, character: str):
        return self.characters.get(character)

    def getFirstAfterCursor(self):
        cursor_position = self.cursor.getPosition()
        positions = self.canvas.getDrawables().keys()

        sorted_x = sorted((position[0] for position in positions if position[1]
                           == cursor_position[1] and position[0] >= cursor_position[0]), reverse=True)

        if len(sorted_x) > 0:
            return sorted_x.pop()

    def getLastBeforeCursor(self):
        cursor_position = self.cursor.getPosition()
        positions = self.canvas.getDrawables().keys()

        sorted_x = sorted(position[0] for position in positions if position[1]
                          == cursor_position[1] and position[0] <= cursor_position[0])

        if len(sorted_x) > 0:
            return sorted_x.pop()

    def snapCursorToLastBeforeCursor(self):
        final_x = self.getLastBeforeCursor()

        if final_x != None:
            while final_x < 0:
                self.scrollLeft()
                final_x += self.unit_size_x

            self.cursor.setX(final_x)

            return True
        else:
            return False

    def snapCursorToFirstAfterCursor(self):
        final_x = self.getFirstAfterCursor()

        if final_x != None:
            while final_x > self.getLimitX():
                self.scrollRight()
                final_x -= self.unit_size_x

            self.cursor.setX(final_x)

            return True
        else:
            return False

    def carriageReturn(self):
        scrolled = False

        while self.canvas.getDrawable(self.cursor.getPosition()):
            scrolled = self.moveCursorBackwards()

        if scrolled:
            self.scrollRight()
        else:
            self.moveCursorForwards()

    def carriageLimit(self):
        scrolled = False

        while self.canvas.getDrawable(self.cursor.getPosition()):
            scrolled = self.moveCursorForwards()

        if scrolled:
            self.scrollLeft()
        else:
            self.moveCursorBackwards()

    def newLine(self):
        if self.snapCursorToLastBeforeCursor():
            self.carriageReturn()

        self.moveCursorDownwards()

    def fillString(self, string: str):
        for character in string:
            if character in '\x00\r':
                continue

            space_character = self.characters.get(' ')
            if space_character:
                if character == '\t':
                    tab = 4
                    for _ in range(tab):
                        self.editUnderCursor(space_character)
                        self.moveCursorForwards()
                    continue

            if character == '\n':
                self.newLine()
                continue

            character_surface = self.characters.get(character)
            if character_surface:
                self.editUnderCursor(character_surface)
                self.moveCursorForwards()

    def getLine(self, cut: bool = False):
        line = ''
        character_items = self.characters.items()

        self.snapCursorToLastBeforeCursor()
        self.carriageReturn()

        while (surface := self.canvas.getDrawable(self.cursor.getPosition())):
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
        drawables = self.canvas.getDrawables().items()
        sorted_drawables_intermediate = sorted(
            [((position[1], position[0]), surface) for position, surface in drawables])
        sorted_drawables = [((position[1], position[0]), surface)
                            for position, surface in sorted_drawables_intermediate]
        character_items = self.characters.items()

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

    def updateTint(self):
        self.tints.rotate()
        self.tint = self.tints[0]
