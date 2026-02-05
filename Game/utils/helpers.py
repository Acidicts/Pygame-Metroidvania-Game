import os
import pygame
from Game.utils.config import get_config

configs = get_config()


def px_to_grid(px):
    if px is None:
        return None
    # If given a tuple (x, y) — convert to integer grid coordinates
    if isinstance(px, tuple):
        return (int(px[0] // configs["tile_size"]), int(px[1] // configs["tile_size"]))
    # If given a single numeric value, return its integer grid index
    try:
        # Handles int/float-like values
        return int(px // configs["tile_size"])
    except Exception:
        # Fallback: attempt to coerce to numbers then compute
        try:
            return int(float(px) // configs["tile_size"])
        except Exception:
            return None


def grid_to_px(grid):
    return grid * configs["tile_size"]


def crop_to_content(surface, bg_color=None, empty_size=(1, 1)):

    # Defensive: ensure pygame mask functions are available (pygame should be initialized by caller)
    try:
        from pygame import mask as _unused
    except Exception:
        # Try to init the modules needed (this is non-invasive if already initialized)
        pygame.init()

    # If bg_color provided, treat that color as transparent by using a copy with that colorkey
    if bg_color is not None:
        tmp = surface.copy()
        try:
            tmp.set_colorkey(bg_color)
        except Exception:
            # Some surfaces may not support set_colorkey; fall back to original surface
            tmp = surface
        mask = pygame.mask.from_surface(tmp)
    else:
        mask = pygame.mask.from_surface(surface)

    try:
        rect = mask.get_bounding_rect()
    except AttributeError:
        # Older pygame versions use get_bounding_rects; fall back to computing from rects list
        rects = mask.get_bounding_rects()
        rect = rects[0] if rects else pygame.Rect(0, 0, 0, 0)

    if rect.width == 0 or rect.height == 0:
        # Fully empty surface: return a small transparent surface
        return pygame.Surface(empty_size, pygame.SRCALPHA)

    # Create a new surface with alpha so we preserve transparency and blit the cropped area
    new_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    new_surf.blit(surface, (0, 0), rect)

    # Preserve colorkey if original had one and new_surf has no alpha
    try:
        ckey = surface.get_colorkey()
        if ckey is not None:
            # If the original had no alpha (colorkey-based transparency), set colorkey on the new surface
            new_surf.set_colorkey(ckey)
    except Exception:
        # ignore surfaces that don't support colorkey/get_colorkey
        pass

    return new_surf


def find_tilemap_for_rect(tilemaps, rect):
    for name, tilemap in tilemaps.items():
        if tilemap.contains_rect(rect):
            return name, tilemap
    return None, None
