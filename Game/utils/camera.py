import pygame

class Camera:
    def __init__(self, width, height):
        self.offset = pygame.Vector2(0, 0)
        self.target_offset = pygame.Vector2(0, 0)
        self.width = width
        self.height = height
        self.smoothing_factor = 0.1  # Lower values = smoother but more lag

    def apply(self, entity):
        return pygame.Rect(
            entity.rect.x - self.offset.x,
            entity.rect.y - self.offset.y,
            entity.rect.width,
            entity.rect.height
        )

    def update(self, target):
        # Calculate target position
        target_x = target.rect.centerx - (self.width // 2)
        target_y = target.rect.centery - (self.height // 2)

        # Apply smoothing to reduce jittering
        self.target_offset.x = target_x
        self.target_offset.y = target_y

        # Smooth interpolation towards target
        self.offset.x += (self.target_offset.x - self.offset.x) * self.smoothing_factor
        self.offset.y += (self.target_offset.y - self.offset.y) * self.smoothing_factor
