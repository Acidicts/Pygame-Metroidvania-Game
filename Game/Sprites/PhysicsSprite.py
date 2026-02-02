import pygame

from Game.Sprites.Sprite import Sprite


class PhysicsSprite(Sprite):
    def __init__(self, image, position, game, velocity=(0, 0), acceleration=(0, 0)):
        super().__init__(image, position)
        self.image = image
        self.game = game
        self.rect = self.image.get_rect(topleft=position)

        # Single source of truth: pos is the float position
        self.pos = pygame.math.Vector2(self.rect.topleft)

        self.velocity = pygame.math.Vector2(velocity)
        self.acceleration = pygame.math.Vector2(acceleration)

        # Gravity in pixels / s^2
        self.gravity = 1200
        self.max_fall_speed = 1200

        # Collision state flags
        self.collisions = {
            "top": False,
            "bottom": False,
            "left": False,
            "right": False
        }

    def _get_solid_tiles_in_rect(self, rect):
        solid_rects = []

        # Debug - only print once
        debug = False

        for tilemap in self.game.tilemaps.values():
            if not tilemap.rendered:
                continue

            tile_size = tilemap.tile_size
            if tile_size <= 0:
                continue

            # Calculate grid bounds - don't clamp to tilemap bounds since tiles can be at any position
            left = int(rect.left // tile_size) - 1
            right = int(rect.right // tile_size) + 1
            top = int(rect.top // tile_size) - 1
            bottom = int(rect.bottom // tile_size) + 1

            if debug:
                print(f"[DEBUG] rect={rect}, grid range x=[{left},{right}] y=[{top},{bottom}]")
                print(f"[DEBUG] tilemap has {len(tilemap.tile_map)} tiles, rendered={tilemap.rendered}")
                # Check for tiles at y=5 (the platform the player should land on)
                tiles_at_y5 = [(k, v) for k, v in tilemap.tile_map.items() if k[1] == 5]
                print(f"[DEBUG] tiles at y=5: {len(tiles_at_y5)}")
                if tiles_at_y5:
                    for k, v in tiles_at_y5[:3]:
                        print(f"  tile {k}: props={v.get('properties')}")
                self._debug_done = True

            for gx in range(left, right + 1):
                for gy in range(top, bottom + 1):
                    tile = tilemap.get_tile(gx, gy)
                    if tile is None:
                        continue

                    # Check if 'solid' in properties.
                    properties = tile.get('properties', [])
                    if "solid" in properties:
                         solid_rects.append(pygame.Rect(gx * tile_size, gy * tile_size, tile_size, tile_size))

        return solid_rects

    def _reset_collisions(self):
        self.collisions = {
            "top": False,
            "bottom": False,
            "left": False,
            "right": False
        }

    def _move_and_collide(self, dx, dy):
        STEPSIZE = 2  # Reduced step size for smoother collision detection

        # Move horizontally with stepping
        remaining_x = dx
        while abs(remaining_x) > 0.01:
            step = max(-STEPSIZE, min(STEPSIZE, remaining_x))

            self.pos.x += step
            self.rect.x = int(round(self.pos.x))

            # Check for collision
            collided = False
            solid_rects = self._get_solid_tiles_in_rect(self.rect)
            for tile_rect in solid_rects:
                if self.rect.colliderect(tile_rect):
                    if step > 0:  # Moving right
                        self.rect.right = tile_rect.left
                        self.collisions["right"] = True
                    else:  # Moving left
                        self.rect.left = tile_rect.right
                        self.collisions["left"] = True
                    self.pos.x = float(self.rect.x)
                    # Only zero out velocity if we were moving in that direction
                    if (step > 0 and self.velocity.x > 0) or (step < 0 and self.velocity.x < 0):
                        self.velocity.x = 0
                    collided = True
                    break

            if collided:
                break
            remaining_x -= step

        # Move vertically with stepping
        remaining_y = dy
        while abs(remaining_y) > 0.01:
            step = max(-STEPSIZE, min(STEPSIZE, remaining_y))

            self.pos.y += step
            self.rect.y = int(round(self.pos.y))

            # Check for collision
            collided = False
            solid_rects = self._get_solid_tiles_in_rect(self.rect)
            for tile_rect in solid_rects:
                if self.rect.colliderect(tile_rect):
                    if step > 0:  # Moving down
                        self.rect.bottom = tile_rect.top
                        self.collisions["bottom"] = True
                    else:  # Moving up
                        self.rect.top = tile_rect.bottom
                        self.collisions["top"] = True
                    self.pos.y = float(self.rect.y)
                    # Only zero out velocity if we were moving in that direction
                    if (step > 0 and self.velocity.y > 0) or (step < 0 and self.velocity.y < 0):
                        self.velocity.y = 0
                    collided = True
                    break

            if collided:
                break
            remaining_y -= step

        # Final sync - keep pos and rect in sync properly
        self.pos.x = self.rect.x
        self.pos.y = self.rect.y

        return dx, dy

    def apply_gravity(self, dt):
        self.velocity.y += self.gravity * dt
        if self.velocity.y > self.max_fall_speed:
            self.velocity.y = self.max_fall_speed

    def update(self, dt):
        if not getattr(self, '_update_debug_done', False):
            self._update_debug_done = True

        self._reset_collisions()

        # Apply acceleration (horizontal only, gravity is separate)
        self.velocity.x += self.acceleration.x * dt

        # Apply gravity
        self.apply_gravity(dt)

        # Calculate movement
        dx = self.velocity.x * dt
        dy = self.velocity.y * dt

        # Move and resolve collisions
        self._move_and_collide(dx, dy)

        # Sync position after collision resolution
        self.pos.x = float(self.rect.x)
        self.pos.y = float(self.rect.y)

    def draw(self, screen, offset):
        super().draw(screen, offset)
