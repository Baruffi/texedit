from collections import deque
from typing import Deque, List, Tuple, TypeVar, Generic

import pygame

from classes.canvas import Canvas
from classes.cursor import Cursor

T = TypeVar('T')


class Editor(Generic[T]):

    def __init__(self, cursor: Cursor, canvas: Canvas[T], unit_size_x: int = 1, unit_size_y: int = 1, grid_size_x: int = 2, grid_size_y: int = 2):
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

    def setCanvasDrawables(self, *drawables: Tuple[Tuple[int, int], T]):
        self.canvas.setDrawables(dict(drawables))

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

    def editUnderCursor(self, drawable: T):
        position = self.cursor.getPosition()

        self.canvas.setDrawable(position, drawable)

    def deleteUnderCursor(self):
        position = self.cursor.getPosition()

        self.canvas.deleteDrawable(position)


class TextEditor(Editor[Tuple[str, pygame.Surface, Tuple[int, ...], Tuple[int, ...]]]):
    def __init__(self, font: pygame.font.Font, grid_size_x: int = 2, grid_size_y: int = 2):
        cursor_surface = font.render(
            '|', False, (255, 255, 255), (0, 0, 0))
        flash_surface = font.render(' ', False, (255, 255, 255), (0, 0, 0))

        cursor = Cursor(cursor_surface, 0, 0, flash_surface)
        canvas = Canvas[Tuple[str, pygame.Surface,
                              Tuple[int, ...], Tuple[int, ...]]]({})
        tints: Deque[Tuple[int, ...]] = deque([(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
                                               (255, 255, 0), (255, 0, 255), (0, 255, 255)])
        unit_size_x = cursor_surface.get_width()
        unit_size_y = cursor_surface.get_height()

        super().__init__(cursor, canvas, unit_size_x,
                         unit_size_y, grid_size_x, grid_size_y)

        self.font = font

        self.tints = tints

        self.tint = tints[0]

        self.state = -1

        self.history: List[Tuple[Tuple[int, int],
                                 Tuple[Tuple[Tuple[int, int], Tuple[str, pygame.Surface, Tuple[int, ...], Tuple[int, ...]]]]]] = []

    def getTint(self):
        return self.tint

    def renderCharacter(self, character: str, color: pygame.Color = (255, 255, 255), background: pygame.Color = (0, 0, 0)):
        return self.font.render(character, False, color, background)

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

            if character == '\t':
                tab = 4
                for _ in range(tab):
                    self.editUnderCursor(('', self.renderCharacter(
                        ' '), self.getUnitSizes(), self.getTint()))
                    self.moveCursorForwards()
                continue

            if character == '\n':
                self.newLine()
                continue

            self.editUnderCursor((character, self.renderCharacter(
                character), self.getUnitSizes(), self.getTint()))
            self.moveCursorForwards()

    def getLine(self, cut: bool = False):
        line = ''

        self.snapCursorToLastBeforeCursor()
        self.carriageReturn()

        while (drawable := self.canvas.getDrawable(self.cursor.getPosition())):
            line += drawable[0]

            self.moveCursorForwards()

        if cut:
            for _ in line:
                self.moveCursorBackwards()
                self.deleteUnderCursor()

        return line

    def getContent(self):
        content = ''
        positions = self.canvas.getDrawables().keys()

        sorted_yx = sorted(((position[1], position[0])
                            for position in positions))

        last_y = -1

        for y, x in sorted_yx:
            if -1 != last_y != y:
                content += '\n' * ((y - last_y) // self.unit_size_y)

            drawable = self.canvas.getDrawable((x, y))

            if drawable:
                content += drawable[0]
                last_y = y

        return content

    def cursorFlash(self):
        self.cursor.updateSurface()

    def updateTint(self):
        self.tints.rotate()
        self.tint = self.tints[0]

    def record(self):
        new_state = tuple(self.cursor.getPosition()), tuple(
            self.canvas.getDrawables().items())

        if len(self.history) == 0 or self.history[self.state] != new_state:
            self.state += 1

            while self.state < len(self.history):
                self.history.pop()

            self.history.append(new_state)

    def load(self):
        cursor_pos, drawables = self.history[self.state]

        self.setCursorPosition(*cursor_pos)
        self.setCanvasDrawables(*drawables)

    def undo(self):
        if len(self.history) > self.state > 0:
            self.state -= 1
            self.load()

    def redo(self):
        if len(self.history) > self.state + 1 > 0:
            self.state += 1
            self.load()
