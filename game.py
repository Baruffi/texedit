from tkinter import Tk
from tkinter.filedialog import askopenfile, asksaveasfile
import pygame
from drawable import Canvas, TextEditor

CURSORFLASH: int = pygame.USEREVENT + 1


def setup():
    pygame.init()
    pygame.display.set_caption('Texedit.py')
    pygame.key.set_repeat(150, 30)

    font = pygame.font.Font('graphics/fonts/kongtext/kongtext.ttf', 24)

    text_editor = TextEditor(Canvas({}), font, 24)

    text_editor_size = text_editor.getWidth(), text_editor.getHeight()

    screen = pygame.display.set_mode(text_editor_size)

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
            if pygame.key.get_mods() & pygame.KMOD_CTRL:
                if event.key == pygame.K_UP:
                    text_editor.scrollUp()

                if event.key == pygame.K_DOWN:
                    text_editor.scrollDown()

                if event.key == pygame.K_c:
                    copy_text = ''
                    empty_character = text_editor.getEmptyCharacter()
                    canvas = text_editor.getCanvas()
                    character_items = text_editor.getCharacters().items()

                    while (drawable_id := canvas.getIdByPosition(text_editor.getCursor().getPosition())):
                        drawable = canvas.getDrawable(drawable_id)

                        if drawable.getSurface() == empty_character:
                            break

                        text_editor.moveCursorBackwards()

                    text_editor.moveCursorForwards()

                    while (drawable_id := canvas.getIdByPosition(text_editor.getCursor().getPosition())):
                        drawable = canvas.getDrawable(drawable_id)

                        if drawable.getSurface() == empty_character:
                            break

                        for character, character_surface in character_items:
                            if drawable.getSurface() == character_surface:
                                copy_text += character
                                break

                        text_editor.moveCursorForwards()

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
                        copy_text = ''
                        empty_character = text_editor.getEmptyCharacter()
                        drawables = text_editor.getCanvas().getDrawables().values()
                        character_items = text_editor.getCharacters().items()
                        character_bool = True

                        for drawable in drawables:
                            if character_bool and drawable.getSurface() == empty_character:
                                copy_text += '\n'
                                character_bool = False
                            else:
                                for character, character_surface in character_items:
                                    if drawable.getSurface() == character_surface:
                                        copy_text += character
                                        character_bool = True
                                        break

                        file.write(copy_text)

                if event.key == pygame.K_l:
                    text_editor.setCursorPosition(0, 0)
                    text_editor.resetCanvas()

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
                text_editor.moveCursorDownwards()
                text_editor.setCursorPosition(0)

            if event.key == pygame.K_DELETE:
                empty_character = text_editor.getEmptyCharacter()
                text_editor.editUnderCursor(empty_character)

            if event.key == pygame.K_BACKSPACE:
                text_editor.moveCursorBackwards()

                empty_character = text_editor.getEmptyCharacter()
                text_editor.editUnderCursor(empty_character)

            if event.key == pygame.K_INSERT:
                text_editor.moveCursorForwards()

                empty_character = text_editor.getEmptyCharacter()
                text_editor.editUnderCursor(empty_character)

            if event.key == pygame.K_HOME:
                text_editor.setCursorPosition(0)

            if event.key == pygame.K_END:
                limit_x = text_editor.getLimitX()
                text_editor.setCursorPosition(limit_x)

            if event.key == pygame.K_PAGEUP:
                height = text_editor.getHeight() // text_editor.getUnitSizeY()
                for _ in range(height):
                    text_editor.scrollUp()

            if event.key == pygame.K_PAGEDOWN:
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
                character = text_editor.getCharacter(event.unicode)
                if character:
                    text_editor.editUnderCursor(character)
                    text_editor.moveCursorForwards()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_mouse_x = (mouse_x // text_editor.getUnitSizeX()
                            ) * text_editor.getUnitSizeX()
            grid_mouse_y = (mouse_y // text_editor.getUnitSizeY()
                            ) * text_editor.getUnitSizeY()
            grid_mouse_pos = grid_mouse_x, grid_mouse_y

            text_editor.setCursorPosition(*grid_mouse_pos)

        if event.type == CURSORFLASH:
            text_editor.cursorFlash()


def draw(text_editor: TextEditor, screen: pygame.Surface):
    screen.fill((0, 0, 0))

    drawables = text_editor.getCanvas().getDrawables().values()
    cursor = text_editor.getCursor()

    for drawable in drawables:
        screen.blit(drawable.getSurface(), drawable.getPosition())

    screen.blit(cursor.getSurface(), cursor.getPosition())

    pygame.display.update()


def loop():
    screen, text_editor = setup()

    while True:
        update(text_editor)
        draw(text_editor, screen)


loop()
