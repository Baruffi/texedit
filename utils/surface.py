from typing import Tuple

import pygame


def getTinted(surface: pygame.Surface, color: Tuple[int, ...]):
    surface = surface.copy().convert()

    surface.fill(color, special_flags=pygame.BLEND_RGBA_ADD)

    return surface


def getScaled(surface: pygame.Surface, size: Tuple[int, int]):
    surface = surface.copy().convert()

    return pygame.transform.scale(surface, size)
