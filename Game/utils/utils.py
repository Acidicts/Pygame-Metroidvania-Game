import pygame
import os
import json

BASE_IMG_PATH = "Game/assets/"
TILE_SIZE = 32

def load_image(path, colorkey=None, size=None):
    img = pygame.image.load(BASE_IMG_PATH + path)
    if size is not None:
        img = pygame.transform.scale(img, size)
    try:
        img = img.convert_alpha()
    except FileNotFoundError:
        pass
    if colorkey is not None:
        img.set_colorkey(colorkey)
    if "icon_" in path:
        img = pygame.transform.scale(img, (16, 16))
    return img


def load_images(path):
    images = []
    for img_name in os.listdir(BASE_IMG_PATH + path):
        images.append(load_image(path + '/' + str(img_name)))
    return images

def load_json_as_dict(path):
    with open(BASE_IMG_PATH + path, 'r') as f:
        data = json.load(f)
    return data

class SpriteSheet:
    def __init__(self, path, tile_size=None, cut=None, colorkey=None, scale=1.0):
        self.images = {}
        self.path = path
        self.tile_size = tile_size
        self.colorkey = colorkey
        self.scale = scale

        self.cut = cut if cut is not None else {"0": (0, 0, 64, 64)}

        if tile_size:
            self.get_images()
        else:
            self.cut_images()

    def get_images(self):
        base = load_image(self.path, colorkey=self.colorkey)
        rect = base.get_rect()

        for y in range(0, rect.height, self.tile_size):
            for x in range(0, rect.width, self.tile_size):
                temp = pygame.Surface((self.tile_size, self.tile_size), flags=pygame.SRCALPHA)
                temp.blit(base, (0, 0), pygame.Rect(x, y, self.tile_size, self.tile_size))
                if self.scale != 1.0:
                    new_size = (int(self.tile_size * self.scale), int(self.tile_size * self.scale))
                    temp = pygame.transform.scale(temp, new_size)
                self.images[(x, y)] = temp

    def cut_images(self):
        base = load_image(self.path, colorkey=self.colorkey)
        for key, rect_vals in self.cut.items():
            # be defensive: allow JSON lists/tuples and skip invalid entries
            try:
                x, y, w, h = tuple(rect_vals)
            except (TypeError, ValueError):
                continue
            if w > 0 and h > 0:
                temp = pygame.Surface((w, h), flags=pygame.SRCALPHA)
                temp.blit(base, (0, 0), pygame.Rect(x, y, w, h))
                if self.scale != 1.0:
                    new_size = (int(w * self.scale), int(h * self.scale))
                    temp = pygame.transform.scale(temp, new_size)
                self.images[str(key)] = temp

    def get_images_list(self):
        sprites = []
        for key in self.images.keys():
            sprites.append(self.images[key])
        return sprites

    def get_debug_image(self):
        base = load_image(self.path, colorkey=self.colorkey)
        base_copy = base.copy()
        rect = base_copy.get_rect()
        pygame.draw.rect(base_copy, (255, 0, 0), rect, 4)

        for key, (x, y, w, h) in self.cut.items():
            if w > 0 and h > 0:
                temp_rect = pygame.Rect(x, y, w, h)
                pygame.draw.rect(base_copy, (255, 0, 0), temp_rect, 4)

        return base_copy

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images))
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]
