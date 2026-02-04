import pygame
from Game.Sprites.PhysicsSprite import PhysicsSprite

class Enemy(PhysicsSprite):
    def __init__(self, image, position, game):
        super().__init__(image, position, game)
        self.health = 3
        self.max_health = 3
        self.immunity = 0  # Time remaining for immunity after taking damage
        self.sprite_group = None

        self.hurt = 0
        self.hurt_cooldown = 0.2

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
                self.immunity = 0.5  # 0.5 seconds of immunity after taking damage

    def die(self):
        """Method to handle enemy death"""
        # Could add death effects, sounds, drops, etc. here
        self.kill()  # Remove enemy from all sprite groups

    def kill(self):
        # Call parent kill to remove from all groups
        super().kill()

    def apply_knockback(self, vec):
        self.velocity.x += vec.x
        self.velocity.y += vec.y

    def update(self, dt):
        if self.hurt > 0:
            self.hurt -= dt
            if self.hurt < 0:
                self.hurt = 0
        # Update immunity timer
        if self.immunity > 0:
            self.immunity -= dt
            if self.immunity < 0:
                self.immunity = 0

        super().update(dt)

    def draw(self, screen, offset):
        # support offset as sequence (tuple/list) or pygame.Vector2
        try:
            offx = offset[0]
            offy = offset[1]
        except Exception:
            try:
                offx = offset.x
                offy = offset.y
            except Exception:
                offx = 0
                offy = 0
        # Use hasattr to check if pos attribute exists (for PhysicsSprite compatibility)
        if hasattr(self, 'pos'):
            pos = (int(self.pos.x - offx), int(self.pos.y - offy))
        else:
            pos = (int(self.rect.x - offx), int(self.rect.y - offy))
        if self.hurt == 0:
            screen.blit(self.image, pos)
        elif self.hurt > 0:
            img = self.image.copy()
            img.fill((255, 255, 255, 0.1), special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(img, pos)
        else:
            self.hurt = 0
