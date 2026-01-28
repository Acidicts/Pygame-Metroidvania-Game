import pygame
from Game.utils.helpers import px_to_grid


class PhysicsSprite(pygame.sprite.Sprite):
    def __init__(self, image, position, game, velocity=(0, 0), acceleration=(0, 0)):
        super().__init__()
        self.image = image
        self.game = game
        self.rect = self.image.get_rect(topleft=position)
        self.pre_fram_rect = self.rect.copy()

        self.velocity = pygame.math.Vector2(velocity)
        self.acceleration = pygame.math.Vector2(acceleration)

        self.collisions = {
            "top": [False, False, False],
            "bottom": [False, False, False],
            "left": [False, False, False],
            "right": [False, False, False]
        }

    def _solid_tiles_in_rect(self, rect):
        solid_rects = []
        for tilemap in self.game.tilemaps.values():
            tile_size = tilemap.tile_size
            if tile_size <= 0:
                continue
            left = rect.left // tile_size - 1
            right = rect.right // tile_size + 1
            top = rect.top // tile_size - 1
            bottom = rect.bottom // tile_size + 1

            for gx in range(int(left), int(right) + 1):
                for gy in range(int(top), int(bottom) + 1):
                    tile = tilemap.get_tile(gx, gy)
                    if tile is None:
                        continue
                    if "solid" not in tile.get('properties', []):
                        continue
                    solid_rects.append(pygame.Rect(gx * tile_size, gy * tile_size, tile_size, tile_size))
        return solid_rects

    def _reset_collisions(self):
        self.collisions = {
            "top": [False, False, False],
            "bottom": [False, False, False],
            "left": [False, False, False],
            "right": [False, False, False]
        }

    def _resolve_axis(self, axis):
        solid_rects = self._solid_tiles_in_rect(self.pre_fram_rect)
        hits = [tile for tile in solid_rects if self.pre_fram_rect.colliderect(tile)]
        if not hits:
            return

        if axis == "x":
            if self.velocity.x > 0:
                nearest = min(tile.left for tile in hits)
                self.pre_fram_rect.right = nearest
                self.collisions["right"] = [True, True, True]
            elif self.velocity.x < 0:
                nearest = max(tile.right for tile in hits)
                self.pre_fram_rect.left = nearest
                self.collisions["left"] = [True, True, True]
            self.velocity.x = 0
        else:
            if self.velocity.y > 0:
                nearest = min(tile.top for tile in hits)
                self.pre_fram_rect.bottom = nearest
                self.collisions["bottom"] = [True, True, True]
            elif self.velocity.y < 0:
                nearest = max(tile.bottom for tile in hits)
                self.pre_fram_rect.top = nearest
                self.collisions["top"] = [True, True, True]
            self.velocity.y = 0

    def update(self, dt):
        self._reset_collisions()

        # prepare candidate rect
        self.pre_fram_rect = self.rect.copy()

        # integrate physics
        self.velocity += self.acceleration * dt
        self.pre_fram_rect.x += int(self.velocity.x * dt)
        self._resolve_axis("x")

        self.pre_fram_rect.y += int(self.velocity.y * dt)
        self._resolve_axis("y")

        # commit position
        self.rect = self.pre_fram_rect.copy()
