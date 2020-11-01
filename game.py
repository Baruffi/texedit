from typing import Dict
from tkinter import Tk
from tkinter.filedialog import askopenfile, asksaveasfile
import pygame
from drawable import Canvas, Drawable

pygame.init()
pygame.display.set_caption('Texedit.py')
pygame.key.set_repeat(150, 30)

unit_size_x = 24
unit_size_y = 25

screen = pygame.display.set_mode((unit_size_x * 24, unit_size_y * 24))

pygame.scrap.init()
pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

font = pygame.font.Font('graphics/fonts/kongtext/kongtext.ttf', 24)

CURSORFLASH = pygame.USEREVENT + 1
pygame.time.set_timer(CURSORFLASH, 500)

cursor_is_flashing = False
cursor_surface = font.render('|', False, (255, 255, 255), (0, 0, 0))
cursor_flash = font.render(' ', False, (255, 255, 255), (0, 0, 0))
cursor = Drawable(cursor_surface, 0, 0)

empty_surface = pygame.Surface((unit_size_x, unit_size_y))

characters = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasadfghjklzxcvbnm,.;:\\/[]{}()0123456789*+-=<>_&%$#@!?"\'´`~^ '

character_dict: Dict[str, pygame.Surface] = {}

for character in characters:
    character_dict[character] = font.render(
        character, False, (255, 255, 255), (255, 0, 255))

canvas = Canvas({})

tk_root = Tk()
tk_root.withdraw()


def update():
    global cursor_is_flashing

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

        if event.type == pygame.KEYDOWN:
            cursor_x, cursor_y = cursor.getPosition()
            max_x = (screen.get_width() // unit_size_x) * unit_size_x - unit_size_x
            max_y = (screen.get_height() // unit_size_y) * unit_size_y

            if pygame.key.get_mods() & pygame.KMOD_CTRL:
                if event.key == pygame.K_UP:
                    canvas.updatePositions(0, unit_size_y)

                if event.key == pygame.K_DOWN:
                    canvas.updatePositions(0, -unit_size_y)

                if event.key == pygame.K_c:
                    copy_text = ''
                    current_x, current_y = cursor_x, cursor_y

                    while (drawable_id := canvas.getIdByPosition((current_x, current_y))):
                        drawable = canvas.getDrawable(drawable_id)

                        if drawable.getSurface() == empty_surface:
                            break

                        if current_x > 0:
                            current_x -= unit_size_x
                        else:
                            current_x = max_x
                            current_y -= unit_size_y

                    if current_x < max_x:
                        current_x += unit_size_x
                    else:
                        current_x = 0
                        current_y += unit_size_y

                    while (drawable_id := canvas.getIdByPosition((current_x, current_y))):
                        drawable = canvas.getDrawable(drawable_id)

                        if drawable.getSurface() == empty_surface:
                            break

                        for character, character_surface in character_dict.items():
                            if drawable.getSurface() == character_surface:
                                copy_text += character
                                break

                        if current_x < max_x:
                            current_x += unit_size_x
                        else:
                            current_x = 0
                            current_y += unit_size_y

                    pygame.scrap.put(pygame.SCRAP_TEXT, copy_text.encode('ascii'))

                if event.key == pygame.K_v:
                    for character in pygame.scrap.get(pygame.SCRAP_TEXT).decode('ascii'):
                        if character in '\x00\r':
                            continue

                        if character == '\t':
                            for _ in range(4):
                                cursor_x, cursor_y = cursor.getPosition()
                                below_cursor = canvas.getIdByPosition((cursor_x, cursor_y)) or 'empty' + str(canvas.getLength())
                                canvas.updateOrCreate(below_cursor, character_dict[' '], (cursor_x, cursor_y))

                                if cursor_x < max_x:
                                    cursor.setPosition((cursor_x + unit_size_x, cursor_y))
                                elif cursor_y + unit_size_y < max_y:
                                    cursor.setPosition((0, cursor_y + unit_size_y))
                                else:
                                    canvas.updatePositions(0, -unit_size_y)
                                    cursor.setPosition((0, cursor_y))
                            continue

                        if character == '\n':
                            for _ in range((max_x + unit_size_x - cursor.getX()) // unit_size_x):
                                cursor_x, cursor_y = cursor.getPosition()
                                below_cursor = canvas.getIdByPosition((cursor_x, cursor_y)) or 'empty' + str(canvas.getLength())
                                canvas.updateOrCreate(below_cursor, empty_surface, (cursor_x, cursor_y))

                                if cursor_x < max_x:
                                    cursor.setPosition((cursor_x + unit_size_x, cursor_y))
                                elif cursor_y + unit_size_y < max_y:
                                    cursor.setPosition((0, cursor_y + unit_size_y))
                                else:
                                    canvas.updatePositions(0, -unit_size_y)
                                    cursor.setPosition((0, cursor_y))
                            continue

                        cursor_x, cursor_y = cursor.getPosition()
                        below_cursor = canvas.getIdByPosition((cursor_x, cursor_y)) or 'empty' + str(canvas.getLength())
                        canvas.updateOrCreate(below_cursor, character_dict[character], (cursor_x, cursor_y))

                        if cursor_x < max_x:
                            cursor.setPosition((cursor_x + unit_size_x, cursor_y))
                        elif cursor_y + unit_size_y < max_y:
                            cursor.setPosition((0, cursor_y + unit_size_y))
                        else:
                            canvas.updatePositions(0, -unit_size_y)
                            cursor.setPosition((0, cursor_y))

                if event.key == pygame.K_o:
                    if (f := askopenfile('r')):
                        t: str = f.read()

                        for character in t:
                            if character in '\x00\r':
                                continue

                            if character == '\t':
                                for _ in range(4):
                                    cursor_x, cursor_y = cursor.getPosition()
                                    below_cursor = canvas.getIdByPosition((cursor_x, cursor_y)) or 'empty' + str(canvas.getLength())
                                    canvas.updateOrCreate(below_cursor, character_dict[' '], (cursor_x, cursor_y))

                                    if cursor_x < max_x:
                                        cursor.setPosition((cursor_x + unit_size_x, cursor_y))
                                    elif cursor_y + unit_size_y < max_y:
                                        cursor.setPosition((0, cursor_y + unit_size_y))
                                    else:
                                        canvas.updatePositions(0, -unit_size_y)
                                        cursor.setPosition((0, cursor_y))
                                continue

                            if character == '\n':
                                for _ in range((max_x + unit_size_x - cursor.getX()) // unit_size_x):
                                    cursor_x, cursor_y = cursor.getPosition()
                                    below_cursor = canvas.getIdByPosition((cursor_x, cursor_y)) or 'empty' + str(canvas.getLength())
                                    canvas.updateOrCreate(below_cursor, empty_surface, (cursor_x, cursor_y))

                                    if cursor_x < max_x:
                                        cursor.setPosition((cursor_x + unit_size_x, cursor_y))
                                    elif cursor_y + unit_size_y < max_y:
                                        cursor.setPosition((0, cursor_y + unit_size_y))
                                    else:
                                        canvas.updatePositions(0, -unit_size_y)
                                        cursor.setPosition((0, cursor_y))
                                continue

                            cursor_x, cursor_y = cursor.getPosition()
                            below_cursor = canvas.getIdByPosition((cursor_x, cursor_y)) or 'empty' + str(canvas.getLength())
                            canvas.updateOrCreate(below_cursor, character_dict[character], (cursor_x, cursor_y))

                            if cursor_x < max_x:
                                cursor.setPosition((cursor_x + unit_size_x, cursor_y))
                            elif cursor_y + unit_size_y < max_y:
                                cursor.setPosition((0, cursor_y + unit_size_y))
                            else:
                                canvas.updatePositions(0, -unit_size_y)
                                cursor.setPosition((0, cursor_y))

                if event.key == pygame.K_s:
                    if (f := asksaveasfile('w')):
                        copy_text = ''
                        character_bool = True

                        for drawable in canvas.getDrawables().values():
                            if character_bool and drawable.getSurface() == empty_surface:
                                copy_text += '\n'
                                character_bool = False
                            else:
                                for character, character_surface in character_dict.items():
                                    if drawable.getSurface() == character_surface:
                                        copy_text += character
                                        character_bool = True
                                        break

                        f.write(copy_text)

                if event.key == pygame.K_l:
                    canvas.setDrawables({})
                    cursor.setPosition((0, 0))

                continue

            if event.key == pygame.K_LEFT:
                if cursor_x - unit_size_x >= 0:
                    cursor.setPosition((cursor_x - unit_size_x, cursor_y))
                elif cursor_y - unit_size_y >= 0:
                    cursor.setPosition((max_x, cursor_y - unit_size_y))
                else:
                    cursor.setPosition((max_x, cursor_y))
                    canvas.updatePositions(0, unit_size_y)

            if event.key == pygame.K_RIGHT:
                if cursor_x + unit_size_x < max_x:
                    cursor.setPosition((cursor_x + unit_size_x, cursor_y))
                elif cursor_y + unit_size_y < max_y:
                    cursor.setPosition((0, cursor_y + unit_size_y))
                else:
                    cursor.setPosition((0, cursor_y))
                    canvas.updatePositions(0, -unit_size_y)

            if event.key == pygame.K_UP:
                if cursor_y - unit_size_y >= 0:
                    cursor.setPosition((cursor_x, cursor_y - unit_size_y))
                else:
                    canvas.updatePositions(0, unit_size_y)

            if event.key == pygame.K_DOWN:
                if cursor_y + unit_size_y < max_y:
                    cursor.setPosition((cursor_x, cursor_y + unit_size_y))
                else:
                    canvas.updatePositions(0, -unit_size_y)

            if event.key == pygame.K_RETURN:
                if cursor_y + unit_size_y < max_y:
                    cursor.setPosition((0, cursor_y + unit_size_y))
                else:
                    cursor.setPosition((0, cursor_y))
                    canvas.updatePositions(0, -unit_size_y)

            if event.key == pygame.K_BACKSPACE:
                if cursor_x > 0:
                    behind_cursor = canvas.getIdByPosition((cursor_x - unit_size_x, cursor_y))

                    if behind_cursor:
                        canvas.getDrawable(behind_cursor).setSurface(empty_surface)
                        cursor.setPosition((cursor_x - unit_size_x, cursor_y))
                else:
                    behind = max_x, cursor_y - unit_size_y
                    behind_cursor = canvas.getIdByPosition(behind)

                    if behind_cursor:
                        canvas.getDrawable(behind_cursor).setSurface(empty_surface)

                        if behind[1] < 0:
                            canvas.updatePositions(0, unit_size_y)
                            cursor.setPosition((max_x, cursor_y))
                        else:
                            cursor.setPosition(behind)

            if event.key == pygame.K_DELETE:
                below_cursor = canvas.getIdByPosition((cursor_x, cursor_y))

                if below_cursor:
                    canvas.updateSurface(
                        below_cursor, empty_surface)

            if event.key == pygame.K_INSERT:
                if cursor_x < max_x:
                    ahead_cursor = canvas.getIdByPosition((cursor_x + unit_size_x, cursor_y))

                    if ahead_cursor:
                        canvas.getDrawable(ahead_cursor).setSurface(empty_surface)
                        cursor.setPosition((cursor_x + unit_size_x, cursor_y))
                else:
                    ahead = 0, cursor_y + unit_size_y
                    ahead_cursor = canvas.getIdByPosition(ahead)

                    if ahead_cursor:
                        canvas.getDrawable(ahead_cursor).setSurface(empty_surface)

                        if ahead[1] >= max_y:
                            canvas.updatePositions(0, -unit_size_y)
                            cursor.setPosition((0, cursor_y))
                        else:
                            cursor.setPosition(ahead)

            if event.key == pygame.K_HOME:
                cursor.setPosition((0, cursor_y))

            if event.key == pygame.K_END:
                cursor.setPosition((max_x, cursor_y))

            if event.key == pygame.K_PAGEUP:
                canvas.updatePositions(0, max_y)

            if event.key == pygame.K_PAGEDOWN:
                canvas.updatePositions(0, -max_y)

            if event.key == pygame.K_TAB:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    if cursor_x - 4 * unit_size_x >= 0:
                        cursor.setPosition((cursor_x - 4 * unit_size_x, cursor_y))
                    else:
                        cursor.setPosition((0, cursor_y))
                else:
                    if cursor_x + 4 * unit_size_x < max_x:
                        cursor.setPosition((cursor_x + 4 * unit_size_x, cursor_y))
                    else:
                        cursor.setPosition((max_x, cursor_y))

            if event.unicode in character_dict.keys():
                below_cursor = canvas.getIdByPosition((cursor_x, cursor_y)) or 'empty' + str(canvas.getLength())
                canvas.updateOrCreate(below_cursor, character_dict[event.unicode], (cursor_x, cursor_y))

                if cursor_x < max_x:
                    cursor.setPosition((cursor_x + unit_size_x, cursor_y))
                elif cursor_y + unit_size_y < max_y:
                    cursor.setPosition((0, cursor_y + unit_size_y))
                else:
                    canvas.updatePositions(0, -unit_size_y)
                    cursor.setPosition((0, cursor_y))

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_mouse_x = (mouse_x // unit_size_x) * unit_size_x
            grid_mouse_y = (mouse_y // unit_size_y) * unit_size_y
            grid_mouse_pos = grid_mouse_x, grid_mouse_y

            cursor.setPosition(grid_mouse_pos)

        if event.type == CURSORFLASH:
            cursor_is_flashing = not cursor_is_flashing
            cursor.setSurface(cursor_flash) if cursor_is_flashing else cursor.setSurface(
                cursor_surface)


def draw():
    canvas.draw(screen)
    screen.blit(cursor.getSurface(), cursor.getPosition())


# loop do jogo

while True:
    update()
    draw()
    pygame.display.update()
