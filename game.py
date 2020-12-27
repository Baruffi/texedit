from tkinter import Tk
from tkinter.filedialog import askopenfile, asksaveasfile

import pygame

from classes.editor import TextEditor
from constants import CURSORFLASH
from utils.surface import getScaled, getTinted


def setup():
    pygame.init()
    pygame.display.set_caption('Texedit.py')
    pygame.key.set_repeat(150, 30)

    font = pygame.font.Font('graphics/fonts/kongtext/kongtext.ttf', 24)

    text_editor = TextEditor(font, 24, 24)

    text_editor_size = text_editor.getWidth(), text_editor.getHeight()

    screen = pygame.display.set_mode(text_editor_size, flags=pygame.RESIZABLE)

    pygame.scrap.init()
    pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

    pygame.time.set_timer(CURSORFLASH, 500)

    tk_root = Tk()
    tk_root.withdraw()

    return screen, text_editor


def update(text_editor: TextEditor):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

        if event.type == pygame.KEYDOWN:
            text_editor.record()

            if pygame.key.get_mods() & pygame.KMOD_ALT:
                if event.key == pygame.K_c:
                    text_editor.updateTint()

                if event.key == pygame.K_MINUS:
                    x, y = text_editor.getUnitSizes()
                    text_editor.setUnitSizes(x // 2, y // 2)
                    x, y = text_editor.getGridSizes()
                    text_editor.setGridSizes(x * 2, y * 2)

                if event.key == pygame.K_EQUALS:
                    x, y = text_editor.getUnitSizes()
                    text_editor.setUnitSizes(x * 2, y * 2)
                    x, y = text_editor.getGridSizes()
                    text_editor.setGridSizes(x // 2, y // 2)

                continue

            if pygame.key.get_mods() & pygame.KMOD_CTRL:
                if event.key == pygame.K_LEFT:
                    text_editor.scrollLeft()

                if event.key == pygame.K_RIGHT:
                    text_editor.scrollRight()

                if event.key == pygame.K_UP:
                    text_editor.scrollUp()

                if event.key == pygame.K_DOWN:
                    text_editor.scrollDown()

                if event.key == pygame.K_c:
                    copy_text = text_editor.getLine()

                    pygame.scrap.put(pygame.SCRAP_TEXT,
                                     copy_text.encode('ascii'))

                if event.key == pygame.K_x:
                    copy_text = text_editor.getLine(True)

                    pygame.scrap.put(pygame.SCRAP_TEXT,
                                     copy_text.encode('ascii'))

                if event.key == pygame.K_v:
                    text: str = pygame.scrap.get(
                        pygame.SCRAP_TEXT).decode('ascii')
                    text_editor.fillString(text)

                if event.key == pygame.K_o:
                    if (file := askopenfile('r')):
                        text: str = file.read()
                        text_editor.fillString(text)

                if event.key == pygame.K_s:
                    if (file := asksaveasfile('w')):
                        content = text_editor.getContent()

                        file.write(content)

                if event.key == pygame.K_l:
                    text_editor.setCursorPosition(0, 0)
                    text_editor.resetCanvas()

                if event.key == pygame.K_z:
                    text_editor.undo()

                if event.key == pygame.K_y:
                    text_editor.redo()

                continue

            if event.key == pygame.K_LEFT:
                text_editor.moveCursorBackwards()

            if event.key == pygame.K_RIGHT:
                text_editor.moveCursorForwards()

            if event.key == pygame.K_UP:
                text_editor.moveCursorUpwards()

            if event.key == pygame.K_DOWN:
                text_editor.moveCursorDownwards()

            if event.key == pygame.K_RETURN:
                text_editor.newLine()

            if event.key == pygame.K_DELETE:
                text_editor.deleteUnderCursor()
                text_editor.moveCursorForwards()

            if event.key == pygame.K_BACKSPACE:
                text_editor.moveCursorBackwards()
                text_editor.deleteUnderCursor()

            if event.key == pygame.K_HOME:
                if text_editor.canvas.getDrawable(text_editor.cursor.getPosition()):
                    text_editor.carriageReturn()
                else:
                    text_editor.snapCursorToLastBeforeCursor()

            if event.key == pygame.K_END:
                if text_editor.canvas.getDrawable(text_editor.cursor.getPosition()):
                    text_editor.carriageLimit()
                else:
                    text_editor.snapCursorToFirstAfterCursor()

            if event.key == pygame.K_PAGEUP:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    width = text_editor.getWidth() // text_editor.getUnitSizeX()

                    for _ in range(width):
                        text_editor.scrollLeft()
                else:
                    height = text_editor.getHeight() // text_editor.getUnitSizeY()

                    for _ in range(height):
                        text_editor.scrollUp()

            if event.key == pygame.K_PAGEDOWN:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    width = text_editor.getWidth() // text_editor.getUnitSizeX()

                    for _ in range(width):
                        text_editor.scrollRight()
                else:
                    height = text_editor.getHeight() // text_editor.getUnitSizeY()

                    for _ in range(height):
                        text_editor.scrollDown()

            if event.key == pygame.K_TAB:
                unit_size_x = text_editor.getUnitSizeX()
                limit_x = text_editor.getLimitX()
                cursor_x = text_editor.getCursor().getX()

                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    if cursor_x - 4 * unit_size_x >= 0:
                        tab = 4
                        for _ in range(tab):
                            text_editor.moveCursorLeft()
                    else:
                        text_editor.setCursorPosition(0)
                else:
                    if cursor_x + 4 * unit_size_x < limit_x:
                        tab = 4
                        for _ in range(tab):
                            text_editor.moveCursorRight()
                    else:
                        text_editor.setCursorPosition(limit_x)

            if event.unicode:
                text_editor.fillString(event.unicode)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    text_editor.scrollLeft()
                else:
                    text_editor.scrollUp()
            elif event.button == 5:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    text_editor.scrollRight()
                else:
                    text_editor.scrollDown()
            elif event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_mouse_x = (mouse_x // text_editor.getUnitSizeX()
                                ) * text_editor.getUnitSizeX()
                grid_mouse_y = (mouse_y // text_editor.getUnitSizeY()
                                ) * text_editor.getUnitSizeY()
                grid_mouse_pos = grid_mouse_x, grid_mouse_y

                text_editor.setCursorPosition(*grid_mouse_pos)

        if event.type == pygame.VIDEORESIZE:
            new_grid_x = event.w // text_editor.getUnitSizeX()
            new_grid_y = event.h // text_editor.getUnitSizeY()

            text_editor.setGridSizes(new_grid_x, new_grid_y)

            pygame.display.set_mode(
                (text_editor.getWidth(), text_editor.getHeight()), flags=pygame.RESIZABLE)

        if event.type == CURSORFLASH:
            text_editor.cursorFlash()


def draw(text_editor: TextEditor, screen: pygame.Surface):
    screen.fill((0, 0, 0))

    drawables = text_editor.getCanvas().getDrawables().items()
    cursor = text_editor.getCursor()
    tint = text_editor.getTint()
    scale = text_editor.getUnitSizes()

    for position, drawable in drawables:
        screen.blit(
            getTinted(getScaled(drawable[1], drawable[2]), drawable[3]), position)

    screen.blit(getTinted(getScaled(cursor.getSurface(), scale),
                          tint), cursor.getPosition())

    pygame.display.update()


def loop():
    screen, text_editor = setup()

    while True:
        update(text_editor)
        draw(text_editor, screen)


loop()
