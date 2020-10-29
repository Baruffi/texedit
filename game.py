from typing import Dict
import pygame
from drawable import Canvas, Drawable

pygame.init()
pygame.display.set_caption('Texedit.py')
pygame.key.set_repeat(100, 25)

unit_size_x = 24
unit_size_y = 25

screen = pygame.display.set_mode((unit_size_x * 24, unit_size_y * 24))

font = pygame.font.Font('graphics/fonts/kongtext/kongtext.ttf', 24)

CURSORFLASH = pygame.USEREVENT + 1
pygame.time.set_timer(CURSORFLASH, 500)

cursor_is_flashing = False
cursor_surface = font.render('|', False, (255, 255, 255), (0, 0, 0))
cursor_flash = font.render(' ', False, (255, 255, 255), (0, 0, 0))
cursor = Drawable(cursor_surface, 0, 0)

empty_surface = pygame.Surface((unit_size_x, unit_size_y))

characters = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasadfghjklzxcvbnm,.;\\/[]{}()0123456789*+-=<>&%$#@!?"\' '

character_dict: Dict[str, pygame.Surface] = {}

for character in characters:
    character_dict[character] = font.render(
        character, False, (255, 255, 255), (255, 0, 255))

canvas = Canvas({'empty0': Drawable(empty_surface, 0, 0)})


def update():
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
                continue

            if event.key == pygame.K_LEFT:
                if cursor_x - unit_size_x >= 0:
                    cursor.setPosition((cursor_x - unit_size_x, cursor_y))
                elif cursor_y - unit_size_y >= 0:
                    cursor.setPosition((max_x, cursor_y - unit_size_y))
                else:
                    canvas.updatePositions(0, unit_size_y)

            if event.key == pygame.K_RIGHT:
                if cursor_x + unit_size_x < max_x:
                    cursor.setPosition((cursor_x + unit_size_x, cursor_y))
                elif cursor_y + unit_size_y < max_y:
                    cursor.setPosition((0, cursor_y + unit_size_y))
                else:
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

            if event.unicode in character_dict.keys():
                below_cursor = canvas.getIdByPosition((cursor_x, cursor_y))

                if below_cursor:
                    canvas.updateSurface(
                        below_cursor, character_dict[event.unicode])
                else:
                    len_drawables = len(canvas.getDrawables().keys())
                    new_empty_zone = 'empty' + str(len_drawables)

                    canvas.setDrawable(new_empty_zone, Drawable(
                        character_dict[event.unicode], cursor_x, cursor_y))

                if cursor_x < max_x:
                    cursor.setPosition((cursor_x + unit_size_x, cursor_y))
                elif cursor_y + unit_size_y < max_y:
                    cursor.setPosition((0, cursor_y + unit_size_y))
                else:
                    canvas.updatePositions(0, -unit_size_y)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_mouse_x = (mouse_x // unit_size_x) * unit_size_x
            grid_mouse_y = (mouse_y // unit_size_y) * unit_size_y
            grid_mouse_pos = grid_mouse_x, grid_mouse_y

            if not canvas.getIdByPosition(grid_mouse_pos):
                len_drawables = len(canvas.getDrawables().keys())
                new_empty_zone = 'empty' + str(len_drawables)
                canvas.setDrawable(new_empty_zone, Drawable(
                    empty_surface, grid_mouse_x, grid_mouse_y))

            cursor.setPosition(grid_mouse_pos)

        if event.type == CURSORFLASH:
            global cursor_is_flashing
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
