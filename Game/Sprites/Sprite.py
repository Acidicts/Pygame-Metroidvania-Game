import pygame

class Sprite:
    def __init__(self, image, position):
        self.image = image
        self.rect = self.image.get_rect(topleft=position)

    def draw(self, surf, offset):
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
        surf.blit(self.image, pos)

    def update(self, dt):
        pass