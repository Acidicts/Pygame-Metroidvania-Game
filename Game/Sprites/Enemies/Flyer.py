import pygame
from Game.Sprites.Enemy import Enemy

class Flyer(Enemy):
    def __init__(self, img, pos, game, tilemap=None):
        super().__init__(img, pos, game)
        self.speed = 50
        self.health = 3
        self.damage = 1
        self.direction = pygame.Vector2(-1, 1)  # Start moving right only
        self.move_timer = 0
        self.move_interval = 2.0
        self.tilemap = tilemap

        # Gravity shouldn't affect flying enemies
        self.gravity = 0
        self.max_fall_speed = 0

    def _move_and_collide(self, dx, dy):
        # Store original position
        old_x, old_y = self.pos.x, self.pos.y

        # Move horizontally
        self.pos.x += dx
        self.rect.x = int(round(self.pos.x))

        # Check horizontal collision
        solid_rects = self._get_solid_tiles_in_rect(self.rect)
        for tile_rect in solid_rects:
            if self.rect.colliderect(tile_rect):
                # Revert horizontal movement
                self.pos.x = old_x
                self.rect.x = int(round(self.pos.x))
                # Reverse horizontal direction
                self.direction.x *= -1
                self.velocity.x = self.speed * self.direction.x
                self.collisions["right" if dx > 0 else "left"] = True
                break

        # Move vertically
        self.pos.y += dy
        self.rect.y = int(round(self.pos.y))

        # Check vertical collision
        solid_rects = self._get_solid_tiles_in_rect(self.rect)
        for tile_rect in solid_rects:
            if self.rect.colliderect(tile_rect):
                # Revert vertical movement
                self.pos.y = old_y
                self.rect.y = int(round(self.pos.y))
                # Reverse vertical direction
                self.direction.y *= -1
                self.velocity.y = self.speed * self.direction.y
                self.collisions["bottom" if dy > 0 else "top"] = True
                break

        # Final sync
        self.pos.x = self.rect.x
        self.pos.y = self.rect.y

        return dx, dy

    def apply_gravity(self, dt):
        # Flying enemies don't apply gravity
        pass

    def take_damage(self, damage):
        if self.hurt != 0:
            return  # Currently in hurt cooldown, ignore damage

        self.hurt = self.hurt_cooldown

        if self.immunity <= 0:
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.die()  # Call custom death method
            else:
                # Reverse direction when taking damage
                self.direction.x *= -1
                self.direction.y *= -1
                self.immunity = 0.5  # 0.5 seconds of immunity after taking damage


    def update(self, dt):
        if self.hurt != 0:
            self.hurt -= dt
            if self.hurt < 0:
                self.hurt = 0
        if self.immunity != 0:
            self.immunity -= dt
            if self.immunity < 0:
                self.immunity = 0

        if not getattr(self, '_update_debug_done', False):
            self._update_debug_done = True

        self._reset_collisions()

        # Periodically change direction for more interesting movement
        self.move_timer += dt
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            # Randomly change direction
            import random
            if random.random() < 0.3:  # 30% chance to change Y direction
                self.direction.y *= -1
            if random.random() < 0.3:  # 30% chance to change X direction
                self.direction.x *= -1

        # Set velocity based on direction and speed
        self.velocity.x = self.speed * self.direction.x
        self.velocity.y = self.speed * self.direction.y

        # Calculate movement
        dx = self.velocity.x * dt
        dy = self.velocity.y * dt

        # Move and resolve collisions
        self._move_and_collide(dx, dy)

        # Sync position after collision resolution
        self.pos.x = float(self.rect.x)
        self.pos.y = float(self.rect.y)